# Plantilla «sitio de estudio» · specs v0.2 (7-nov-2026)

Specs de un sitio privado de estudio de los **principios de la computación**: inicio de sesión → elegir un tema
→ página del tema con pestañas de contenido → todo desplegado en Google Cloud.

Describen la **arquitectura mínima y necesaria**. Son autosuficientes: se construye desde cero con ellas, sin
código previo.

## Estructura

| Pieza | Qué es |
|---|---|
| Login | Dos perfiles (admin y tester), cuentas creadas solo por invitación de un solo uso |
| «Elige un tema» (`/`) | Una tarjeta por tema |
| Página de tema (`/t/{tema}`) | Pestañas declaradas por tema; por defecto **Práctica** (interactiva, anotable) y **Mapa** (esquema conceptual, solo lectura) |
| Anotaciones | Por **sección** del tema y, si la lección lo anuncia, por ejercicio |
| `sitio/temas.json` | Lista cerrada de lo que se publica |
| Contenido | Lecciones y mapas en HTML de un solo archivo |
| Nube | Cloud Run + Firestore + Artifact Registry + Cloud Build en un proyecto propio |

Temas iniciales: **CPU (alto nivel)**, **ALU**, **Lógica booleana y circuitos lógicos**. Se agregan otros
editando `temas.json`, sin tocar el código.

## Documentos

| Archivo | Qué fija |
|---|---|
| `01-pantallas-y-rutas.md` | Pantallas, navegación y rutas HTTP |
| `02-servidor-datos-seguridad.md` | Stack, módulos, API, Firestore y seguridad |
| `03-contenido-y-temas.md` | Manifiesto de temas, contrato de los HTML de contenido, versiones y anotaciones |
| `04-nube-y-despliegue.md` | Proyecto GCP, cuentas de servicio, imagen, Cloud Run, invitaciones y costos |
| `05-pruebas-y-orden-de-trabajo.md` | Pruebas mínimas, criterios de aceptación y fases para construirlo |

## Fuera del mínimo

- Registro abierto, recuperación de contraseña y más de dos perfiles.
- Guardar en el servidor el avance de cada persona.
- Biblioteca de lecturas (descrita como módulo opcional al final de `03`).

## Convenciones

- `{PROYECTO}` = nombre visible (ej. «Principios-Comp-01»). `{GCP}` = id del proyecto en GCP (ej. `principios-comp-01`).
- `{REGION}` = `us-central1`, salvo que se decida otra.
- Las rutas de archivos son relativas a la raíz del repositorio nuevo.
- Cada decisión que se tome se anota con su clave (`P-1`, `P-2`…) en `docs/sitio/decisiones.md` del
  repositorio nuevo.
