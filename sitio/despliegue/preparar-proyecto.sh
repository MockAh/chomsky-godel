#!/usr/bin/env bash
# F5 · Preparación del proyecto en Google Cloud (spec 04 §2–3). Se corre UNA vez, a mano.
#
#   sitio/despliegue/preparar-proyecto.sh
#
# Muestra cada comando y lo corre solo si respondes «s». Si uno falla (p. ej. porque ya
# existe), pregunta si sigues. Todos llevan --project explícito: no cambia el proyecto
# activo de tu gcloud (que puede ser de otro trabajo).
#
# Variables (con valores por defecto, P-26):
#   PROYECTO=chomsky-godel  REGION=us-central1  PRESUPUESTO=100MXN
set -uo pipefail
cd "$(dirname "$0")/../.."

PROYECTO=${PROYECTO:-chomsky-godel}
REGION=${REGION:-us-central1}
PRESUPUESTO=${PRESUPUESTO:-100MXN}
RUN=sitio-run@$PROYECTO.iam.gserviceaccount.com
BUILD=sitio-build@$PROYECTO.iam.gserviceaccount.com
P="--project=$PROYECTO"

paso() {  # paso "qué hace" comando...
  echo
  echo "── $1"
  printf '   $'; printf ' %q' "${@:2}"; echo
  read -r -p "   ¿Correrlo? [s/N/q] " r
  case "$r" in
    s|S) "${@:2}" || { read -r -p "   Falló. ¿Seguir con el siguiente? [s/N] " r2; [[ $r2 == [sS] ]] || exit 1; } ;;
    q|Q) echo "Detenido."; exit 0 ;;
    *) echo "   (saltado)" ;;
  esac
}

if [[ ! -t 0 ]]; then
  echo "Este script pide confirmación en cada paso: córrelo en tu propia terminal (no con «!» desde Claude)." >&2
  exit 2
fi

echo "Proyecto: $PROYECTO · Región: $REGION · Presupuesto: $PRESUPUESTO"
echo "Cuenta activa de gcloud: $(gcloud config get-value account 2>/dev/null)"

# 1. Proyecto y facturación
paso "Crear el proyecto (si el ID está tomado, sal con q y corre con PROYECTO=otro-id)" \
  gcloud projects create "$PROYECTO" --name="chomsky-godel"
echo; echo "Cuentas de facturación disponibles:"
gcloud billing accounts list --format="table(name,displayName,open)"
read -r -p "ID de la cuenta de facturación a usar (formato XXXXXX-XXXXXX-XXXXXX): " CUENTA
[[ $CUENTA =~ ^[0-9A-F]{6}-[0-9A-F]{6}-[0-9A-F]{6}$ ]] || { echo "Cuenta no válida; detenido." >&2; exit 1; }
paso "Ligar el proyecto a la facturación" \
  gcloud billing projects link "$PROYECTO" --billing-account="$CUENTA"

# 2. Servicios
paso "Habilitar Cloud Run, Cloud Build, Artifact Registry, Firestore y Presupuestos" \
  gcloud services enable run.googleapis.com cloudbuild.googleapis.com \
  artifactregistry.googleapis.com firestore.googleapis.com billingbudgets.googleapis.com $P

# 3. Presupuesto con alertas al 50 %, 90 % y 100 % (la moneda debe ser la de la cuenta)
paso "Crear el presupuesto de $PRESUPUESTO para este proyecto" \
  gcloud billing budgets create --billing-account="$CUENTA" --display-name="chomsky-godel" \
  --budget-amount="$PRESUPUESTO" --filter-projects="projects/$PROYECTO" \
  --threshold-rule=percent=0.5 --threshold-rule=percent=0.9 --threshold-rule=percent=1.0

# 4. Firestore (modo nativo) con protección contra borrado, y TTL de lo vencido
paso "Crear la base de Firestore en $REGION" \
  gcloud firestore databases create --location="$REGION" --delete-protection $P
for c in sesiones invitaciones intentos; do
  paso "TTL: borrar lo vencido en $c (campo borrar_en)" \
    gcloud firestore fields ttls update borrar_en --collection-group="$c" --enable-ttl --async $P
done

# 5. Repositorio de imágenes, conservando las 3 últimas
paso "Crear el repositorio de imágenes «sitio»" \
  gcloud artifacts repositories create sitio --repository-format=docker --location="$REGION" $P
paso "Política de limpieza: conservar las 3 imágenes más recientes" \
  gcloud artifacts repositories set-cleanup-policies sitio --location="$REGION" \
  --policy=sitio/despliegue/limpieza-imagenes.json $P  # sin --dry-run: la política sí borra

# 6. Cuentas de servicio con permisos mínimos (spec 04 §3)
paso "Crear la cuenta sitio-run (identidad del servicio)" \
  gcloud iam service-accounts create sitio-run --display-name="Sitio en Cloud Run" $P
paso "Crear la cuenta sitio-build (construye la imagen)" \
  gcloud iam service-accounts create sitio-build --display-name="Sitio en Cloud Build" $P
paso "sitio-run: leer y escribir en Firestore" \
  gcloud projects add-iam-policy-binding "$PROYECTO" --member="serviceAccount:$RUN" \
  --role=roles/datastore.user --condition=None
for rol in roles/artifactregistry.writer roles/logging.logWriter roles/storage.objectViewer; do
  paso "sitio-build: $rol" \
    gcloud projects add-iam-policy-binding "$PROYECTO" --member="serviceAccount:$BUILD" \
    --role="$rol" --condition=None
done

echo
echo "Listo. Anota en docs/sitio/decisiones.md (P-5) el ID de proyecto si no fue chomsky-godel."
