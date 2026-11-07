# 05 · Pruebas y orden de trabajo

## 1. Pruebas mínimas (`sitio/pruebas/`, con `pytest` + `httpx`)

`test_cuentas.py` · `crear_app(AlmacenMemoria(), contenido_de_prueba, reloj=falso)`
- Sin sesión: `/`, `/t/x` → 302 `/login`; `/contenido/...` y `/api/...` → 401.
- Login correcto → cookie `__Host-sesion` con `Secure`, `HttpOnly`, `SameSite=Lax`.
- Correo inexistente y contraseña mala dan el **mismo** mensaje.
- 6.º intento en 15 min → 429; pasados 15 min, se vuelve a poder.
- Sesión vencida (reloj + 7 días) → 401 y se borra.
- Invitación: activa una vez; la segunda → 410; vencida → 410; contraseña débil → 422 y el enlace **sigue**
  sirviendo; cuenta activa → `CuentaYaActiva`.
- Cambiar contraseña cierra las demás sesiones.
- POST sin `Origin` o con otro `Origin` → 403.

`test_sitio.py`
- Tema o pestaña inexistentes → 404.
- `/contenido/{tema}/{pestana}` lleva la CSP de contenido; las demás respuestas, la CSP del sitio y los
  encabezados de §5 de `02`.
- `/api/sesion` devuelve los temas en el orden de `temas.json`.
- Anotaciones: guardar, leer, cambiar el hash del contenido → la nota pasa a «anteriores».
- Tester no ve notas del admin; admin sí ve las del tester; nadie ve correos ajenos (`autor` no aparece).
- Exportar: tester → 403; admin → Markdown con el rol, sin correos.
- Sección que no está en el manifiesto → 404 (o 422).

`test_almacen.py`
- Las mismas pruebas de contrato contra `AlmacenMemoria` y contra `AlmacenFirestore` en el emulador de
  Firestore (`gcloud emulators firestore start`, variable `FIRESTORE_EMULATOR_HOST`), con un `prefijo` de
  colecciones por corrida.

`test_armado.py`
- `armar_contenido` se niega con archivos sin commit; con `--permitir-sucio` marca el commit como `-sucio`.
- `armar_imagen` no incluye `.env`, `.invitaciones.txt`, `.venv` ni `pruebas/`.

`recorrido_navegador.py` (Playwright, contra `local.py`): entrar → elegir tema → cambiar de pestaña sin perder
el estado del iframe → escribir una nota → recargar y verla → salir. También a 400 px de ancho.

## 2. Criterios de aceptación

- [ ] Un tester invitado entra con su enlace, crea su contraseña y ve los tres temas.
- [ ] Cada tema abre sus pestañas; cambiar de pestaña no reinicia la práctica.
- [ ] Las notas se guardan solas, sobreviven a recargar y a un despliegue nuevo.
- [ ] Al publicar una versión nueva de una práctica, las notas previas aparecen como «anteriores».
- [ ] El admin baja todas las notas en un Markdown sin correos.
- [ ] Agregar un cuarto tema solo requiere: HTML + entrada en `temas.json` + commit + construir + publicar.
- [ ] La imagen en línea lleva la etiqueta del commit que se aprobó.
- [ ] Nada sale a la nube con cambios sin commit.

## 3. Orden de trabajo sugerido

| Fase | Entrega | Revisión |
|---|---|---|
| F0 | Repositorio nuevo, `.gitignore`, `docs/sitio/decisiones.md` con P-1… | Usuario |
| F1 | `seguridad.py`, `almacen.py`, `app.py` (login, sesión, temas, contenido) + pruebas en memoria | Pruebas en verde |
| F2 | Front: login, activar, temas, tema con pestañas; un tema de muestra; `local.py` | Usuario, en local |
| F3 | Anotaciones por sección + contrato `postMessage` + exportar | Usuario, en local |
| F4 | `almacen_firestore.py` + pruebas en el emulador | Pruebas en verde |
| F5 | Proyecto GCP, cuentas de servicio, Firestore, Artifact Registry, presupuesto (`04`, §2–3) | Usuario corre o aprueba cada comando |
| F6 | `armar_*`, Dockerfile, `cloudbuild.yaml`, `desplegar.sh`; **construir** | — |
| F7 | **Publicar** (con visto bueno) e `invitar.py` | Usuario |
| F8 | Contenido real de CPU, ALU y lógica booleana | Por tema |

## 4. Decisiones abiertas para el sitio nuevo

| Clave | Pregunta | Propuesta |
|---|---|---|
| P-1 | ¿Iframe del mismo origen o aislado con `sandbox`? | Mismo origen al inicio (como hoy); aislar si se aceptan contenidos de terceros |
| P-2 | Nombres de las pestañas | «Práctica» y «Mapa»; configurables por tema |
| P-3 | ¿Más de 2 perfiles (ej. varios estudiantes)? | No en el mínimo. Si se abre, agregar rol `estudiante` y que el admin vea las notas por persona |
| P-4 | ¿Guardar el avance de cada persona en el servidor? | No en el mínimo |
| P-5 | Nombre del proyecto e id de GCP | `{PROYECTO}` / `{GCP}` por definir |
| P-6 | ¿Partir de código existente? | No: escribirlo desde estas specs, en un repositorio nuevo y con historial propio |
