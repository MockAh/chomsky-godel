# chomsky-godel

Repositorio del programa de estudio de **Ingeniería en Sistemas y Ciberseguridad** de Guillermo, y del
sitio privado donde viven sus lecciones interactivas. Todo en español.

Hay dos partes:

| Parte | Carpeta | Qué es |
|---|---|---|
| **Estudio** (lo central) | `estudio/`, `retos/` | Perfil, plan, progreso, bitácora de sesiones, reportes y retos. Memoria del programa entre sesiones. |
| **Sitio** | `sitio/`, `temas/`, `docs/` | Sitio web (FastAPI + Firestore en Cloud Run) que publica las lecciones de `temas/`. Specs en `docs/plantilla-sitio-estudio/`, decisiones en `docs/sitio/decisiones.md`. |

## Sesiones de estudio

El estudiante entra desde el escritorio (Claude Code en WSL) o desde el teléfono (Claude Code en la nube).
Cada sesión empieza en frío: **la memoria es `estudio/`**.

- Si quiere estudiar, continuar la clase o resolver microtareas → skill **tutor**.
- Si quiere conversar libre o pide un «reporte» → skill **tutor-maestro**.
- Al terminar («cierre») o si pregunta dónde va → skill **escriba**. Toda sesión de estudio termina con
  el Escriba: si el estudiante se despide sin pedirlo, ofrécelo en una línea.
- Si solo saluda sin decir qué quiere, lee `estudio/progreso.md` y ofrece en una línea: seguir con el
  Tutor (y en qué tema), conversar con el Tutor Maestro, o el reto pendiente.

Formato por defecto en sesiones de estudio: respuestas cortas, aptas para pantalla de teléfono.

## Trabajo en el sitio

- Pruebas: `cd sitio && .venv/bin/python -m pytest -q`.
- Probar en local: `sitio/.venv/bin/python sitio/local.py --puerto 8090` (el 8080 lo usa otro proyecto).
- Orden de trabajo: fases F0–F8 de `docs/plantilla-sitio-estudio/05-pruebas-y-orden-de-trabajo.md`.
  F0–F3 hechas; sigue F4 (Firestore).
- Toda decisión nueva se anota en `docs/sitio/decisiones.md` con su clave P-n.
- **Publicar = desplegar, y solo con visto bueno explícito del estudiante.** Nunca despliegues por tu cuenta.
- Cambios al contenido de `temas/` (p. ej. lo que pida `estudio/pendientes-contenido.md`): en una rama,
  subiendo la `version` de la pestaña en `sitio/temas.json`, con pruebas y una revisión visual en
  navegador; entran solo con aprobación del estudiante.

## Datos personales

- `docs/bitacoras-estudio/` y `docs/notas-altas/` son material en bruto, **fuera de git** (P-8).
- En archivos versionados, el estudiante es «Guillermo»: nunca su nombre completo ni sus correos.
