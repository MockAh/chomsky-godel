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

Retos de fase: trabajo en `retos/fase-N/`, herramientas en `retos/herramientas/` (ver `retos/README.md`).

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

## Estado y próximos pasos (al 2026-11-23)

Hecho: sitio F0–F3 (servidor, front con login 3D, anotaciones), capa de estudio (`estudio/`, skills),
herramientas de retos (paso 2) y Fase 1 del estudio cerrada (2026-11-23; sigue Fase 2, C). Plan acordado con el estudiante, en orden:

1. **Paso 3 · GitHub privado (P-20, P-22, P-23): hecho el 2026-11-23.** Repo privado
   `MockAh/chomsky-godel`, autor «Guillermo» + noreply (config local). Pendiente (P-22): el `push` usó un
   token clásico guardado en `~/.git-credentials`; cambiarlo por el fine-grained y revocar el clásico.
   No usar `gh auth login`.
2. **Paso 3b · Claude Code en la nube:** entorno con script de preparación
   (`retos/herramientas/preparar-entorno.sh`, Python del sitio). Verificar antes en la documentación qué
   permite el entorno (paquetes, red).
3. **Paso 4 · Sitio en línea:** F4 (Firestore + emulador; requiere Java y `cloud-firestore-emulator`),
   F5–F7. Decidir P-21 (publicar con PR + despliegue automático, o a mano).
4. **Paso 5 · Agente de contenido:** atender `estudio/pendientes-contenido.md` (Mapa CPU, ALU 3D) en ramas
   con aprobación. Resolver P-7 (propuesta nueva: `script-src 'self'` en la CSP de contenido).

