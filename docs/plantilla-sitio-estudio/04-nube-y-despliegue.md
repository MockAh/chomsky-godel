# 04 · Nube y despliegue

## 1. Esquema

```
 equipo local                         Google Cloud · proyecto {GCP} · {REGION}
 ───────────                          ───────────────────────────────────────────
 git (commit)                         Cloud Build  ──(cuenta sitio-build)──▶ Artifact Registry
   │                                     ▲                                   repo «sitio», guarda 3 imágenes
 armar_imagen.py → build/sitio-imagen ───┘ «construir»                             │
                                                                                   ▼ «publicar»
 invitar.py ──(gcloud, credenciales del admin)──▶ Firestore ◀──(cuenta sitio-run)── Cloud Run «sitio»
                                                   usuarios, sesiones,             0–2 instancias,
                                                   invitaciones, intentos,         URL pública *.run.app
                                                   anotaciones (TTL)
 Facturación: presupuesto con alerta (ej. $100 MXN ≈ $5 USD)
```

Sin GitHub, sin CI y sin dominio propio: el despliegue es manual y siempre con visto bueno del admin.
**Publicar = desplegar**: lo que está en línea es lo que ven los dos.

## 2. Preparación del proyecto (una sola vez)

Cada comando es una tarea; correrlos uno por uno y revisar la salida.

```bash
# Proyecto y facturación
gcloud projects create {GCP}
gcloud billing projects link {GCP} --billing-account=<CUENTA>
gcloud config set project {GCP}

# Servicios
gcloud services enable run.googleapis.com cloudbuild.googleapis.com artifactregistry.googleapis.com firestore.googleapis.com

# Firestore (modo nativo) con protección contra borrado
gcloud firestore databases create --location={REGION} --delete-protection

# Borrado automático de lo vencido
gcloud firestore fields ttls update borrar_en --collection-group=sesiones --enable-ttl
gcloud firestore fields ttls update borrar_en --collection-group=invitaciones --enable-ttl
gcloud firestore fields ttls update borrar_en --collection-group=intentos --enable-ttl

# Repositorio de imágenes, conservando las 3 últimas
gcloud artifacts repositories create sitio --repository-format=docker --location={REGION}
gcloud artifacts repositories set-cleanup-policies sitio --location={REGION} \
  --policy=sitio/despliegue/limpieza-imagenes.json --no-dry-run
```

`sitio/despliegue/limpieza-imagenes.json`:
```json
[
  {"name": "conservar-3", "action": {"type": "Keep"}, "mostRecentVersions": {"keepCount": 3}},
  {"name": "borrar-resto", "action": {"type": "Delete"}, "condition": {"tagState": "any"}}
]
```

## 3. Cuentas de servicio (permisos mínimos)

| Cuenta | Para qué | Roles |
|---|---|---|
| `sitio-run@{GCP}.iam.gserviceaccount.com` | Identidad del servicio en Cloud Run | `roles/datastore.user` |
| `sitio-build@{GCP}.iam.gserviceaccount.com` | Construir la imagen en Cloud Build | `roles/artifactregistry.writer`, `roles/logging.logWriter`, `roles/storage.objectViewer` (para leer el código subido) |
| Tu cuenta (admin) | Construir, publicar, invitar | Dueño del proyecto, o como mínimo `roles/run.admin`, `roles/cloudbuild.builds.editor`, `roles/iam.serviceAccountUser` sobre las dos cuentas, `roles/datastore.user` |

```bash
gcloud iam service-accounts create sitio-run
gcloud iam service-accounts create sitio-build
gcloud projects add-iam-policy-binding {GCP} --member=serviceAccount:sitio-run@{GCP}.iam.gserviceaccount.com --role=roles/datastore.user
gcloud projects add-iam-policy-binding {GCP} --member=serviceAccount:sitio-build@{GCP}.iam.gserviceaccount.com --role=roles/artifactregistry.writer
gcloud projects add-iam-policy-binding {GCP} --member=serviceAccount:sitio-build@{GCP}.iam.gserviceaccount.com --role=roles/logging.logWriter
gcloud projects add-iam-policy-binding {GCP} --member=serviceAccount:sitio-build@{GCP}.iam.gserviceaccount.com --role=roles/storage.objectViewer
```

Cloud Run usa `sitio-run`, no la cuenta por defecto de Compute (que tiene permisos de más).

## 4. Imagen

### `armar_imagen.py`
Arma `build/sitio-imagen/` con una **lista cerrada**: `servidor/`, `web/`, `Dockerfile`, `cloudbuild.yaml`,
`requirements.txt` y `contenido/` (de `armar_contenido.py`). Nada más: ni `.env`, ni `.venv`, ni pruebas, ni
el resto del repositorio. Sin `--permitir-sucio` se niega si `sitio/` o el contenido tienen cambios sin commit.

### `sitio/despliegue/Dockerfile`
```dockerfile
FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY servidor servidor
COPY web web
COPY contenido contenido
USER nobody
CMD exec uvicorn servidor.principal:app --host 0.0.0.0 --port ${PORT:-8080} --no-server-header --no-access-log
```

### `sitio/despliegue/cloudbuild.yaml`
```yaml
# Construye la imagen; no despliega.
serviceAccount: projects/$PROJECT_ID/serviceAccounts/sitio-build@$PROJECT_ID.iam.gserviceaccount.com
options:
  logging: CLOUD_LOGGING_ONLY
steps:
  - name: gcr.io/cloud-builders/docker
    args: ["build", "-t", "{REGION}-docker.pkg.dev/$PROJECT_ID/sitio/sitio:${_ETIQUETA}", "."]
images:
  - {REGION}-docker.pkg.dev/$PROJECT_ID/sitio/sitio:${_ETIQUETA}
```

La etiqueta de la imagen es el commit corto (`git rev-parse --short HEAD`): cada versión en línea apunta a un
commit exacto. Tras un commit nuevo hay que **construir** otra vez antes de **publicar**.

## 5. `sitio/desplegar.sh`

```bash
#!/usr/bin/env bash
# Publicar es desplegar: solo con aprobación del admin.
#   sitio/desplegar.sh construir   arma la lista cerrada y construye la imagen; no publica
#   sitio/desplegar.sh publicar    pone en línea la imagen del commit actual
set -euo pipefail
cd "$(dirname "$0")/.."
PROYECTO={GCP}; REGION={REGION}; SERVICIO=sitio
ETIQUETA=$(git rev-parse --short HEAD)
IMAGEN=$REGION-docker.pkg.dev/$PROYECTO/sitio/sitio:$ETIQUETA
case "${1:-}" in
  construir)
    sitio/.venv/bin/python sitio/armar_imagen.py build/sitio-imagen
    gcloud builds submit build/sitio-imagen --project="$PROYECTO" \
      --config=build/sitio-imagen/cloudbuild.yaml --substitutions=_ETIQUETA="$ETIQUETA" ;;
  publicar)
    gcloud run deploy "$SERVICIO" --project="$PROYECTO" --region="$REGION" --image="$IMAGEN" \
      --service-account="sitio-run@$PROYECTO.iam.gserviceaccount.com" \
      --allow-unauthenticated --min-instances=0 --max-instances=2 \
      --cpu=1 --memory=512Mi --concurrency=20 ;;
  *) echo "Uso: $0 construir|publicar" >&2; exit 2 ;;
esac
```

- `--allow-unauthenticated`: la puerta es el login propio del sitio, no IAM.
- `min-instances=0`: con 2 personas, el costo es casi cero; el primer acceso tras un rato tarda unos segundos.
- `max-instances=2`: tope de gasto si alguien abusa de la URL.

## 6. Primeras cuentas: `invitar.py`

```
sitio/.venv/bin/python sitio/invitar.py https://<url-del-servicio>
```
- Lee `ADMIN_CORREO` y `TESTER_CORREO` de `sitio/.env` **sin imprimirlos**.
- Usa las credenciales de `gcloud auth print-access-token` (las del admin), no una llave de servicio.
- Por cada rol: crea la invitación (huella en Firestore, 14 días) o dice «la cuenta ya está activa; sin enlace».
- Escribe `rol: https://…/activar#<ficha>` en `sitio/.invitaciones.txt` (permisos 600) y en pantalla solo
  dice qué pasó con cada rol.
- El admin entrega cada enlace a su persona por un canal privado.

## 7. Uso local: `local.py`

Levanta `http://localhost:8080` con `AlmacenMemoria`, contenido armado con `--permitir-sucio`, una cuenta
admin con contraseña aleatoria impresa en la terminal y un enlace de activación para el tester. Todo se
pierde al apagar. Sirve para revisar pantallas antes de construir.

## 8. Costos esperados (2 personas)

| Servicio | Uso | Costo |
|---|---|---|
| Cloud Run | Escala a 0 | Dentro de la capa gratuita |
| Firestore | Cientos de lecturas/escrituras al día | Dentro de la capa gratuita |
| Artifact Registry | 3 imágenes de ~150 MB | Centavos al mes |
| Cloud Build | Unos minutos por despliegue | Dentro de la capa gratuita |

Con la alerta de presupuesto basta; no hace falta tope duro.

## 9. Registro de despliegues

Cada despliegue se anota (fecha, revisión de Cloud Run, imagen/commit, quién dio el visto bueno) en
`docs/sitio/decisiones.md`, y si el repositorio nuevo tiene esquema de arquitectura, también ahí en el mismo
commit.
