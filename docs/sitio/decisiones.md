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

## Pendientes conocidos

- Ningún HTML de `notas-altas/` envía todavía los mensajes `postMessage` (`03` §3); funcionarán solo con anotaciones por sección hasta adaptarlos.
- Las imágenes deben ir como `data:` URI dentro de cada HTML y comprimidas.
- Posible cuarto tema: lenguajes formales y autómatas (jerarquía de Chomsky, Lindenbaum–Tarski).

## Registro de despliegues

| Fecha | Revisión de Cloud Run | Imagen / commit | Visto bueno |
|---|---|---|---|
