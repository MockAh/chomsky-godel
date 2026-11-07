# 01 · Pantallas y rutas

## 1. Flujo

```
/activar#<ficha>  (primera vez, enlace de un solo uso)
        │ crea contraseña → abre sesión
        ▼
/login ──(correo + contraseña)──▶ /  «Elige un tema»
                                    │ tarjeta por tema
                                    ▼
                                 /t/{tema}
                                 ┌─────────────┬──────────┐
                                 │ Práctica    │  Mapa    │   ← pestañas (temas.json)
                                 └─────────────┴──────────┘
                                 iframe con el HTML del tema
                                 + botón «Anotaciones» (solo en pestañas anotables)
```

Sin sesión, toda página manda a `/login`. Con sesión, `/login` manda a `/`.

## 2. Pantallas

### P1 · Iniciar sesión (`/login`)
- Tarjeta al centro: marca del sitio, título `{PROYECTO}`, campos **Usuario** (correo) y **Contraseña**, botón
  **Iniciar sesión**.
- Error genérico, igual si el correo no existe o si la contraseña está mal: «Usuario o contraseña incorrectos.»
- Tras 5 intentos fallidos en 15 min: «Demasiados intentos. Espera 15 minutos.»
- La tarjeta se sacude al fallar (solo estética).
- No hay «¿Olvidaste tu contraseña?» ni registro abierto.

### P2 · Crear contraseña (`/activar#<ficha>`)
- La ficha va en el **fragmento** (`#`), así no llega a los registros del servidor ni al `Referer`.
- Campos: contraseña nueva y repetirla, con la regla visible: 12 caracteres o más, con mayúscula,
  minúscula, número y símbolo.
- Si el enlace ya se usó o venció: «Este enlace ya se usó o venció.»
- Al crearla, abre sesión y manda a `/`.

### P3 · Elegir tema (`/`)
- Barra superior: marca, correo de la sesión, **Cambiar contraseña**, **Salir**.
- Título «Elige un tema» y una tarjeta por tema, en el orden de `temas.json`: nombre corto, nombre largo y
  línea de versiones (ej. «Práctica v0.3 · Mapa v0.1, en revisión»).
- La lista sale de `GET /api/sesion`; la página no tiene temas escritos a mano.

### P4 · Página de tema (`/t/{tema}`)
- Barra: «‹ Temas», nombre del tema, pestañas, cuenta.
- **Pestañas** con `role="tablist"`, flechas izquierda/derecha para moverse, `#{pestaña}` en la URL
  (`history.replaceState`) para volver a la misma.
- Cada pestaña es un `<iframe>` que carga `/contenido/{tema}/{pestaña}`. **Los iframes se quedan montados**
  al cambiar de pestaña, para no perder el avance del ejercicio; las pestañas que no son la primera se cargan
  la primera vez que se abren.
- Si la pestaña trae `aviso` en el manifiesto (ej. «En revisión»), el sitio lo muestra como etiqueta al inicio
  del contenido, sin modificar el archivo.
- **Anotaciones** (solo pestañas con `"anotable": true`):
  - Botón «Anotaciones» que abre la vista «Todas las anotaciones», ordenada por sección.
  - Una casilla de texto por sección del tema y, si el contenido las anuncia, una por elemento
    (ejercicio, circuito, pregunta…), ver `03`, §3.
  - Guardado automático: 800 ms después de dejar de escribir y al salir del campo; reintento cada 5 s si falla;
    envío final con `fetch(..., {keepalive:true})` al cerrar la página; aviso del navegador si queda algo sin
    guardar.
  - Si la sesión venció (401): «Tu sesión terminó y esto no se guardó. Copia tu texto, vuelve a entrar y pégalo
    aquí.» Nunca se borra lo escrito.
  - Debajo de cada casilla, en un `<details>`, las notas propias de versiones anteriores del contenido.
  - El **admin** ve además las notas del tester y el enlace **Bajar todas** (Markdown). El **tester no ve** las
    del admin.

### Diálogo · Cambiar contraseña (en P3 y P4)
- Pide la actual, la nueva y repetirla. Al cambiarla se cierran las demás sesiones de esa cuenta.

## 3. Rutas HTTP

| Método | Ruta | Sesión | Devuelve |
|---|---|---|---|
| GET | `/login` | no | `login.html` (o 302 a `/` si ya hay sesión) |
| GET | `/activar` | no | `activar.html` |
| GET | `/` | sí (si no, 302 `/login`) | `temas.html` |
| GET | `/t/{tema}` | sí | `tema.html` (404 si el tema no existe) |
| GET | `/contenido/{tema}/{pestana}` | sí (401) | El HTML del contenido, con su CSP propia |
| GET | `/estaticos/*` | no | CSS, JS, iconos, fuentes del sitio |
| GET | `/salud` | no | 204 (para Cloud Run) |
| POST | `/api/login` | no | Cookie de sesión |
| POST | `/api/activar` | no | Cookie de sesión |
| POST | `/api/contrasena` | sí | Cookie nueva; cierra las demás sesiones |
| POST | `/api/logout` | — | Borra la sesión y la cookie |
| GET | `/api/sesion` | sí | `{correo, rol, temas:[…]}` |
| GET | `/api/anotaciones/{tema}` | sí | Notas visibles para ese usuario (ver `02`, §4) |
| PUT | `/api/anotaciones/{tema}/{pestana}/{seccion}` | sí | Guarda la nota de la sección |
| PUT | `/api/anotaciones/{tema}/{pestana}/{seccion}/elemento` | sí | Guarda la nota de un elemento |
| GET | `/api/anotaciones/exportar` | admin | Todas las notas en Markdown, como descarga |

Sin `/docs`, `/redoc` ni `/openapi.json` (se apagan en FastAPI).

## 4. Archivos del front

```
sitio/web/
  login.html  activar.html  temas.html  tema.html
  estaticos/
    comun.js      sesión, salir, cambiar contraseña (lo comparten P3 y P4)
    login.js  activar.js  temas.js  tema.js
    login.css  sitio.css  favicon.svg
    fuentes/      solo fuentes con licencia que permita servirlas, junto con su licencia
```

JavaScript sin frameworks ni paso de compilación. Todo texto que viene del servidor se pone con
`textContent`, nunca con `innerHTML`.
