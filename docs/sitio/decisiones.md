# Decisiones del sitio · chomsky-godel

Registro de decisiones tomadas al construir el sitio desde las specs v0.2
(`docs/plantilla-sitio-estudio/`). Cada una con su clave; las nuevas se agregan al final.

| Clave | Decisión | Estado | Fecha |
|---|---|---|---|
| P-1 | Iframe del **mismo origen**, sin `sandbox`. Se aísla si algún día se aceptan contenidos de terceros. | Tomada (propuesta de la spec) | 2026-11-07 |
| P-2 | Pestañas por defecto **«Práctica»** (anotable) y **«Mapa»** (solo lectura); configurables por tema en `temas.json`. | Tomada (propuesta de la spec) | 2026-11-07 |
| P-3 | Solo dos perfiles: `admin` y `tester`. | Tomada (propuesta de la spec) | 2026-11-07 |
| P-4 | No se guarda en el servidor el avance de cada persona en las lecciones. | Tomada (propuesta de la spec) | 2026-11-07 |
| P-5 | `{PROYECTO}` = **chomsky-godel** (sin diéresis). `{GCP}` = `chomsky-godel` si está libre en GCP; si no, se elige otro en F5 y se anota aquí. | Tomada | 2026-11-07 |
| P-6 | Se escribe desde cero con las specs, sin código previo, con historial propio. | Tomada | 2026-11-07 |
| P-7 | Lecciones 3D que usan Three.js (ALU, silicio, Unidad de Control): la CSP de contenido prohíbe cargar scripts externos. Propuesta: **incrustar** Three.js en cada archivo (~700 KB más por archivo) en vez de abrir la CSP a un CDN. | **Abierta** (se decide en F8) | 2026-11-07 |
| P-8 | No se versionan `docs/bitacoras-estudio/` (perfil y datos personales) ni `docs/notas-altas/` (material en bruto, imágenes de hasta 16 MB). Viven solo en el equipo local; lo que se publique se adapta a `temas/`. | Tomada | 2026-11-07 |
| P-9 | Secciones de cada tema (las casillas de anotaciones) derivadas de los reportes de cierre de las Fases 0 y 1; ver `sitio/temas.json`. | Tomada | 2026-11-07 |
| P-10 | `mecanismo-fc-metafora.html` (presupuesto UNAM) queda fuera: no es material de este sitio. | Tomada | 2026-11-07 |
| P-11 | Estética del sitio: «espacio» oscuro, monoespaciado, cian/magenta/menta, a partir de `docs/notas-diseño/espacio_3d*.html`. No el estilo «Mac 2000s». | Tomada | 2026-11-07 |
| P-12 | Login = espacio 3D navegable con la esfera al centro; clic en la esfera abre el diálogo de credenciales. Hay botón para teclado, Enter abre el diálogo y sin WebGL el diálogo aparece directo. | Tomada | 2026-11-07 |
| P-13 | Three.js 0.160.0 se sirve desde el propio sitio (`sitio/web/estaticos/vendor/three-0.160.0/`, licencia MIT incluida), verificado contra la integridad sha512 del registro npm. La CSP del sitio no cambia. | Tomada | 2026-11-07 |
| P-14 | Contenido inicial: `logica-booleana` (práctica = `15_circuito_A_noB_o_CD`, mapa = `14_compuertas_fisicas`) y `cpu/mapa` = `16_radiografia_computadora`, copiados sin cambios de `notas-altas`. El resto son páginas provisionales. | Tomada | 2026-11-07 |
| P-15 | `local.py` acepta `--puerto` (el 8080 lo puede usar otro proyecto local). | Tomada | 2026-11-07 |
| P-16 | Anotaciones en un panel lateral «Todas las anotaciones» (pantalla completa en móvil). Las notas por elemento se editan en un diálogo propio; el panel muestra su texto y un botón «Editar». | Tomada | 2026-11-07 |
| P-17 | Mensaje `seccion` de una lección: abre el panel en esa sección solo si su pestaña es la activa; no roba el foco del estudiante. | Tomada | 2026-11-07 |
| P-18 | Las páginas provisionales no envían `postMessage`: solo lo hacen las lecciones reales al entrar a una sección o terminar un elemento. | Tomada | 2026-11-07 |
| P-19 | **El estudio es lo central del repo.** `estudio/` (perfil, plan, progreso, sesiones, reportes y notas convertidos a Markdown, sin nombre completo) se versiona; los tutores son skills del repo (`.claude/skills/tutor`, `tutor-maestro`, `escriba`) y `CLAUDE.md` define el arranque y cierre de cada sesión. Revisa P-8: el material en bruto sigue fuera de git. | Tomada | 2026-11-07 |
| P-20 | El repo se sube a **GitHub como privado** para usar Claude Code en la nube desde el teléfono. Cambia la spec `04` («sin GitHub»). Hecho: `github.com/MockAh/chomsky-godel` (privado), primer `push` el 2026-11-23. | **Hecha** | 2026-11-23 |
| P-21 | Forma de publicar: A) PR + merge desde el teléfono con despliegue automático (Cloud Build), o B) a mano desde el escritorio. Recomendado A; mientras el sitio no esté en línea, B. | **Abierta** | 2026-11-07 |
| P-22 | Acceso a GitHub **acotado**: no se usa `gh auth login` (su permiso `repo` alcanza todos los repos). El estudiante crea a mano el repo privado vacío `chomsky-godel` y un **fine-grained token** solo para ese repo (*Contents: Read and write*, con vencimiento); se usa únicamente para `push`. El inicio de sesión de `gh` se canceló sin autorizar (el token viejo de `gh` sigue inválido). **Desviación 2026-11-23:** el primer `push` usó un token *clásico* (`ghp_…`) guardado en `~/.git-credentials` con `credential.helper store` global; el estudiante decidió conservarlo (2026-11-23) y autorizó que Claude haga `push` con él. | Tomada (con desviación aceptada) | 2026-11-23 |
| P-23 | Antes del primer `push`, el autor de todos los commits pasa a nombre «Guillermo» y al correo noreply de GitHub (lo copia el estudiante de *Settings → Emails*), configurado **solo en este repo**; se verifica que no quede el correo institucional en el historial. Hecho el 2026-11-23 (`git filter-branch`, 12 commits; respaldo local borrado). | **Hecha** | 2026-11-23 |
| P-24 | **«Lecciones de Claude»**: en «Elige un tema», una sección aparte con una tarjeta por fase del programa. Cada fase es un tema normal de `temas.json` con `"grupo": "claude"` (campo opcional, `[a-z0-9-]+`; sin él, el tema va en la lista de siempre) y una pestaña anotable «Lección» (`temas/fase-N/leccion.html`); las fases cerradas tienen dos: «Lecciones» (la teoría de la fase, con notas y ejercicios) y su práctica: «Ejercicios» en la Fase 0, «Reto de cierre» (las cinco mini-tareas) en la Fase 1, con el estilo de papel de `docs/ejemplos-html/`. Sus secciones de anotación son las pestañas internas de la lección (en Fase 1, una por capítulo y una por mini-tarea), y la lección las anuncia con `postMessage` tipo `elemento`. El botón flotante de anotar pasa a fondo sólido para leerse sobre lecciones claras. | Tomada (aprobada por el estudiante) | 2026-11-23 |
| P-25 | **F4 · Firestore**: `AlmacenFirestore` (`sitio/servidor/almacen_firestore.py`) cumple el mismo contrato que `AlmacenMemoria`; activar invitación, reemplazar invitaciones, reservar intento, cambiar contraseña y guardar anotación corren en transacciones. `borrar_en` (fecha) es solo para la TTL; el código revisa `expira`. Las pruebas de contrato corren contra los dos almacenes: la fixture `emulador` usa `FIRESTORE_EMULATOR_HOST` si existe o levanta `gcloud emulators firestore start` en `127.0.0.1:8085` (proyecto ficticio `chomsky-godel-pruebas`), con un prefijo de colecciones por prueba; sin Java o sin el emulador, se saltan con aviso. Entrada de Cloud Run: `servidor.principal:app`. | Tomada | 2026-11-23 |

## Pendientes conocidos

- Ningún HTML de `notas-altas/` envía todavía los mensajes `postMessage` (`03` §3); funcionarán solo con anotaciones por sección hasta adaptarlos.
- Las imágenes deben ir como `data:` URI dentro de cada HTML y comprimidas.
- Posible cuarto tema: lenguajes formales y autómatas (jerarquía de Chomsky, Lindenbaum–Tarski).

## Registro de despliegues

| Fecha | Revisión de Cloud Run | Imagen / commit | Visto bueno |
|---|---|---|---|
