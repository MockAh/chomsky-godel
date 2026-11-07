# 02 · Servidor, datos y seguridad

## 1. Stack

| Pieza | Elección | Por qué |
|---|---|---|
| Lenguaje | Python 3.12 | Simple, con buen soporte en Cloud Run y Firestore |
| Web | FastAPI + Uvicorn | Pocas líneas, validación con Pydantic |
| Contraseñas | `argon2-cffi` (Argon2id) | Hash lento y estándar |
| Datos | Firestore (modo nativo) | Cloud Run no guarda archivos entre reinicios; sin servidor que administrar; casi gratis con 2 personas |
| Front | HTML + CSS + JS sin frameworks | Nada que compilar |

`sitio/requirements.txt`:
```
fastapi>=0.115,<1
uvicorn>=0.30,<1
argon2-cffi>=23.1,<26
google-cloud-firestore>=2.16,<3
```
`sitio/requirements-dev.txt`: `-r requirements.txt`, `pytest`, `httpx`, `playwright`.

## 2. Módulos

```
sitio/
  servidor/
    app.py               crear_app(almacen, dir_contenido, reloj=time.time) → FastAPI
    seguridad.py         política de contraseñas, hash, fichas, huellas
    almacen.py           AlmacenMemoria (pruebas y uso local) + excepción CuentaYaActiva
    almacen_firestore.py AlmacenFirestore (mismos métodos, mismas pruebas)
    principal.py         app = crear_app(AlmacenFirestore(), "contenido")   ← entrada en Cloud Run
  armar_contenido.py     copia el contenido declarado y escribe manifiesto.json (ver 03)
  armar_imagen.py        arma la carpeta exacta que sube a Cloud Build (ver 04)
  local.py               levanta todo en http://localhost:8080 con AlmacenMemoria
  invitar.py             crea los enlaces de primera entrada (ver 04)
  desplegar.sh           construir | publicar
  temas.json             lista cerrada de lo que se publica
  web/  pruebas/  despliegue/
```

**Regla de diseño:** `crear_app` recibe el almacén y el reloj. Así las mismas pruebas corren contra memoria y
contra Firestore, y se puede simular el paso del tiempo (sesiones e invitaciones que vencen).

## 3. Interfaz del almacén

Ambas clases implementan exactamente esto:

| Método | Contrato |
|---|---|
| `guardar_usuario(correo, hash, rol)` | Solo para `local.py` y pruebas |
| `obtener_usuario(correo)` | `dict` o `None` |
| `cambiar_contrasena(correo, hash)` | |
| `crear_invitacion(huella, correo, rol, expira)` | Lanza `CuentaYaActiva` si la cuenta ya existe. La nueva invitación anula las anteriores del mismo correo |
| `obtener_invitacion(huella, ahora)` | `None` si no existe o venció |
| `activar_invitacion(huella, hash, ahora)` | Crea la cuenta y borra la invitación **en una sola transacción**; `None` si no es válida |
| `crear_sesion(huella, correo, expira)` / `obtener_sesion(huella)` / `borrar_sesion(huella)` | |
| `borrar_sesiones_de(correo)` | Al cambiar contraseña |
| `reservar_intento(clave, maximo, ventana, ahora)` | Cuenta el intento **antes** de verificar la contraseña (transacción); `False` si se agotaron |
| `limpiar_intentos(clave)` | Tras entrar bien |
| `guardar_anotacion(tema, pestana, seccion, autor, rol, version_hash, version, texto, ahora, elemento=None)` | Una nota por (tema, pestaña, sección, elemento, autor, version_hash); conserva `creada` y actualiza `actualizada` |
| `listar_anotaciones(tema=None)` | Todas, o las de un tema |

## 4. Firestore

| Colección | Id del documento | Campos | Borrado automático (TTL) |
|---|---|---|---|
| `usuarios` | correo | `correo, hash, rol` | — |
| `invitaciones` | sha256(ficha) | `correo, rol, expira, borrar_en` | `borrar_en` |
| `sesiones` | sha256(ficha) | `correo, expira, borrar_en` | `borrar_en` |
| `intentos` | sha256(correo) o sha256("cambio\|"+correo) | `n, inicio, borrar_en` | `borrar_en` |
| `anotaciones` | sha256(tema\|pestana\|seccion\|elemento\|autor\|version_hash) | `tema, pestana, seccion, elemento, autor, rol, version_hash, version, texto, creada, actualizada` | — |

- **Nunca se guarda la ficha de sesión ni la de invitación**, solo su huella sha256. Quien lea la base no
  puede entrar.
- `expira` (número, segundos) es lo que revisa el código; `borrar_en` (fecha) solo sirve para que el TTL de
  Firestore limpie lo vencido. El código no confía en el TTL, que puede tardar hasta un día.
- Las consultas son por igualdad de un campo (`correo`, `tema`): bastan los índices automáticos.
- `elemento` es `null` o `{clave, titulo, tipo, estado}`; `clave` = sha256(seccion|titulo)[:16].

### Visibilidad de las notas (`GET /api/anotaciones/{tema}`)

| Grupo devuelto | Contiene |
|---|---|
| `mias` | Las mías, de la versión vigente del contenido, por sección |
| `mias_elementos` | Las mías, de la versión vigente, por elemento |
| `anteriores` | Las mías de versiones anteriores, no vacías, las más recientes primero |
| `de_otros` | Solo si soy admin: las de las demás cuentas, no vacías |

Hacia afuera, el autor se muestra **por su rol** («Admin», «Tester»), nunca por su correo: se quitan los
campos `autor` y `rol` y se agrega `autor_rol`. Lo mismo en la exportación a Markdown.

## 5. Seguridad (mínimo obligatorio)

**Cuentas**
- Sin registro abierto. Cada cuenta nace de una invitación creada con `invitar.py`.
- Invitación: ficha de 32 bytes (`secrets.token_urlsafe(32)`), un solo uso, vence a los 14 días.
- **Sin recuperación:** una cuenta ya activa no recibe otra invitación. Si se olvida la contraseña, el admin
  borra la cuenta a mano en Firestore y la vuelve a invitar.
- Política: 12 caracteres o más, con mayúscula, minúscula, número y símbolo. Se valida en el servidor.
- Argon2id con los parámetros por defecto de `argon2-cffi`. Si el correo no existe, se verifica contra un hash
  falso, para tardar lo mismo y no revelar qué correos existen.
- Límite: 5 intentos cada 15 min por correo (al entrar) y por cuenta (al cambiar contraseña).

**Sesión**
- Cookie `__Host-sesion`: `Secure`, `HttpOnly`, `SameSite=Lax`, `Path=/`, 7 días.
- En el servidor la sesión se busca por su huella; si venció, se borra.

**Peticiones**
- Todo método que no sea GET/HEAD exige el encabezado `Origin` y que coincida con `Host`; si no, 403
  (protección contra CSRF sin fichas extra).
- Cuerpos validados con Pydantic y con `max_length` en cada campo (texto de nota ≤ 20 000).

**Encabezados en todas las respuestas**
```
Content-Security-Policy: default-src 'self'; frame-src 'self'; base-uri 'none'; form-action 'self'; frame-ancestors 'none'
Cache-Control: no-store
X-Robots-Tag: noindex, nofollow
X-Content-Type-Options: nosniff
Referrer-Policy: same-origin
Strict-Transport-Security: max-age=31536000
```
El contenido de los temas lleva su propia CSP (ver `03`, §2).

**Secretos**
- Los correos de admin y tester viven en `sitio/.env`, fuera de git y fuera de la imagen.
- Los enlaces de invitación se escriben en `sitio/.invitaciones.txt` (permisos 600, fuera de git).
- `.gitignore` incluye: `sitio/.env`, `sitio/.invitaciones.txt`, `sitio/.venv/`, `build/`.
- El contenedor corre como `nobody`; Uvicorn con `--no-server-header --no-access-log`.

**Roles**
| Rol | Puede |
|---|---|
| `admin` | Todo lo del tester + ver notas de otros + exportar |
| `tester` | Ver temas, usar el contenido, escribir y leer sus propias notas |

Los roles solo se asignan en la invitación; no hay pantalla para cambiarlos.
