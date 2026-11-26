# chomsky-godel

*[English version](README.en.md)*

Programa de estudio personal de **Ingeniería en Sistemas y Ciberseguridad**, que va de las matemáticas
al hardware, y de ahí a los sistemas y la seguridad. También contiene el sitio donde se publican sus
lecciones interactivas.

El estudiante es Guillermo, con formación en matemáticas. Estudia con Claude Code en el escritorio (WSL),
con tres *skills* que funcionan como tutores. El repositorio entero es la memoria del programa: cada
sesión empieza en frío y lee `estudio/`.

## Las fases

| Fase | Tema | Estado |
|---|---|---|
| 0 | **El puente:** de la matemática a la lógica de la máquina | Cerrada |
| 1 | **La máquina desnuda:** CPU, memoria, caché, Assembly x86-64 | Cerrada |
| 2 | **El lenguaje del sistema:** C, punteros, memoria manual, primer buffer overflow | En curso |
| 3 | **El sistema operativo:** procesos, permisos, syscalls, Linux por dentro | — |
| 4 | **Las redes:** OSI y TCP/IP, DNS, HTTP, TLS, Wireshark | — |
| 5 | **Fundamentos de ciberseguridad:** criptografía, autenticación, primer CTF | — |
| 6 | **Bifurcación:** ofensivo o defensivo | — |

El plan completo, con los criterios de salida de cada fase, está en
[`estudio/plan-general.md`](estudio/plan-general.md).

## Cómo está organizado

| Carpeta | Qué hay |
|---|---|
| [`estudio/`](estudio/README.md) | Memoria del programa: perfil, plan, progreso, bitácoras de sesión, reportes de cierre |
| [`retos/`](retos/README.md) | El trabajo de los retos de fase (Assembly, C…) y sus herramientas (`ensamblar.sh`, `trazar.sh`) |
| `temas/` | Las lecciones en HTML: Lógica booleana, ALU, CPU y las Fases 0–2, con su versión en inglés (`*.en.html`) |
| `sitio/` | El sitio web que publica `temas/`: FastAPI + Firestore en Cloud Run |
| `docs/` | Especificación del sitio y su registro de decisiones (`docs/sitio/decisiones.md`) |
| `.claude/skills/` | Los tutores: **tutor**, **tutor-maestro** y **escriba** |

## Los tutores

- **Tutor:** da la clase según el plan, con microlecciones, microtareas y retos. La regla es
  *predice primero, verifica después*.
- **Tutor Maestro:** conversación libre de alto nivel, sin temario. También escribe los reportes de
  entendimiento.
- **Escriba:** cierra cada sesión. Registra lo aprendido en `estudio/progreso.md` y en una bitácora.

## El sitio

Es un «museo» de lo hecho y aprendido. Se publica en Cloud Run y tiene dos versiones:

- **Privada:** con inicio de sesión y anotaciones.
- **De solo lectura (P-34):** por un enlace secreto, en español y en inglés (P-35).

**Probar en local:**

```bash
cd sitio && .venv/bin/python -m pytest -q        # pruebas
sitio/.venv/bin/python sitio/local.py --puerto 8090   # servidor local (desde la raíz)
```

Las reglas para escribir lecciones están en [`temas/instrucciones-html.md`](temas/instrucciones-html.md).
Se comprueban con `sitio/revisar_html.py`. El despliegue se hace con `sitio/desplegar.sh`
(`construir`, luego `publicar`).

## Privacidad

El material en bruto (`docs/bitacoras-estudio/`, `docs/notas-altas/`) y los secretos (`sitio/.env`,
invitaciones, la clave del museo) no se versionan.
