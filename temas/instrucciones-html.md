# Instrucciones para editar o crear los HTML del sitio

Cada pestaña del sitio («Práctica», «Mapa», «Lecciones»…) es **un solo archivo HTML** dentro de esta
carpeta `temas/`. Puedes editarlo donde quieras: en otro editor, en otra sesión de Claude o en el
navegador. Para que funcione dentro del sitio, solo tiene que cumplir las reglas de abajo.

El sitio es un **museo** de lo hecho y aprendido (P-29): aquí no se estudia, se exhibe.

---

## 1. El camino, paso a paso

1. **Edita o crea** el HTML.
   - Para una pestaña que ya existe: el archivo está en `temas/<tema>/<pestaña>.html`
     (p. ej. `temas/alu/practica.html`). Para saber cuál es cuál, mira `sitio/temas.json`.
   - Para algo nuevo: déjalo en `temas/<tema>/` con un nombre corto en minúsculas y guiones
     (`[a-z0-9-]`).
   - Si es un borrador de fuera (de `docs/notas-altas/`, de otra sesión…) que todavía usa CDN, también
     sirve: Claude lo adapta (§3).
2. **Revísalo** tú mismo (opcional, tarda un segundo):
   ```
   sitio/.venv/bin/python sitio/revisar_html.py temas/alu/practica.html
   ```
   Dice «bien» o lista los problemas con su línea.
3. **Pídele a Claude** que lo suba. Basta algo como:
   > «Edité `temas/alu/practica.html`, súbelo al sitio» o
   > «Hay un HTML nuevo en `temas/cpu/control.html`, ponlo como pestaña "Unidad de Control" del tema CPU».
4. **Claude hace el resto** (§4) y te lo enseña en local antes de publicar.
5. **Tú das el visto bueno** para publicar. Sin él no se despliega nada.

---

## 2. Las reglas del archivo

| # | Regla | Por qué |
|---|---|---|
| 1 | **Un solo archivo autocontenido.** CSS y JavaScript van dentro del HTML (`<style>`, `<script>`). | El sitio sirve cada pestaña como un archivo suelto. |
| 2 | **Nada de CDNs ni scripts de otros sitios** (jsdelivr, unpkg, cdnjs…). | La regla de seguridad del contenido (CSP) los bloquea. |
| 3 | **Three.js, solo desde el sitio**, con exactamente este `importmap` (ver abajo). Versión **0.160.0**. | Es la copia verificada que vive en `sitio/web/estaticos/vendor/` (P-7). |
| 4 | **Fuentes: solo Google Fonts** (`<link rel="stylesheet" href="https://fonts.googleapis.com/…">`). | Es la única hoja de estilos externa que se permite. |
| 5 | **Imágenes dentro del archivo**: SVG en línea o `data:` URI, comprimidas. | No se pueden cargar imágenes de fuera. |
| 6 | **No pedir nada a la red**: nada de `fetch`, `XMLHttpRequest`, `WebSocket`, `EventSource` ni `Worker`. | La CSP lo bloquea y la lección se quedaría colgada. |
| 7 | **No guardar nada importante en `localStorage`.** | La lección comparte origen con el sitio. |
| 8 | **Que se vea bien en teléfono** (≈390 px de ancho) y en escritorio. | Claude lo revisa en ambos tamaños. |

### El `importmap` para lecciones 3D

```html
<script type="importmap">
{ "imports": {
  "three": "/estaticos/vendor/three-0.160.0/three.module.min.js",
  "three/addons/": "/estaticos/vendor/three-0.160.0/addons/"
} }
</script>
<script type="module">
import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
// …
</script>
```

**Complementos disponibles hoy** (`three/addons/…`):

- `controls/OrbitControls.js`
- `renderers/CSS2DRenderer.js`
- `environments/RoomEnvironment.js`

¿Necesitas otro (p. ej. `loaders/GLTFLoader.js`)? Úsalo con normalidad y avisa: Claude lo agrega
verificado desde npm. Mientras no esté, `revisar_html.py` dirá «no existe en el sitio».

### Mientras editas fuera del sitio

Si abres el archivo directamente en tu navegador (doble clic), las rutas `/estaticos/…` no existen y Three.js
no carga. Tienes dos opciones:

- **Editar con el CDN** (`https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.module.js` y
  `…/examples/jsm/`) y dejar que Claude lo cambie al `importmap` del sitio al subirlo.
- **Verlo con el sitio local**, que ya sirve `/estaticos/` (solo muestra pestañas que estén en
  `sitio/temas.json`): `sitio/.venv/bin/python sitio/local.py --puerto 8090` y abrir `http://localhost:8090`.

---

## 3. Lo que Claude adapta si hace falta

Si el archivo viene de fuera, al copiarlo a `temas/` Claude:

- cambia el `importmap` del CDN por el del sitio;
- limpia la cabecera (si viene de una exportación con `<head>` raro o tema claro forzado);
- quita los mensajes de error que mencionan el CDN;
- revisa que no haya datos personales (nombre completo, correos): en el repo eres «Guillermo».

---

## 4. Lo que hace Claude para subirlo

1. Crea una **rama** para el cambio.
2. Si es una pestaña nueva, la agrega a `sitio/temas.json`. Si ya existía, **sube su `version`**
   (`v0.2` → `v0.3`). Así las anotaciones viejas quedan como «anteriores».
3. Corre `revisar_html.py` y las pruebas (`cd sitio && .venv/bin/python -m pytest -q`).
   El armado se **niega** a construir si algún HTML rompe estas reglas.
4. Lo revisa en un navegador (escritorio, teléfono y dentro del sitio) y te pasa el enlace local.
5. Con tu visto bueno: une la rama, **construye** la imagen y la **publica**
   (`sitio/desplegar.sh construir` y luego `publicar`), y lo anota en `docs/sitio/decisiones.md`.

---

## 5. Versión en inglés (solo en el museo, P-35)

El museo (`/m/<clave>/`) tiene botón **English / Español**. Cada pestaña puede tener su versión en inglés:

1. Copia el archivo con `.en` antes de `.html`: `temas/alu/practica.html` → `temas/alu/practica.en.html`.
2. Traduce los textos (también los que están dentro del JavaScript: etiquetas, tooltips, mensajes),
   pon `<html lang="en">` y deja igual todo lo demás. Términos técnicos en su forma estándar en inglés.
3. Cumple las mismas reglas de §2 (`revisar_html.py` también revisa el `.en.html`).
4. Claude lo declara en `sitio/temas.json`, dentro de la pestaña:
   ```json
   "en": {"etiqueta": "Practice", "archivo": "temas/alu/practica.en.html"}
   ```
   Si la pestaña aún no tiene `archivo` en inglés, el museo en inglés muestra la de español con la etiqueta
   «Spanish only».

Si cambias la versión en español, conviene cambiar también la inglesa (las dos comparten `version`).

---

## 6. Opcional: anotaciones por ejercicio

Si quieres que el sitio ofrezca «Anotar este ejercicio» en un punto concreto de la lección, el HTML
puede avisarle con `postMessage` (detalle en `docs/plantilla-sitio-estudio/03-contenido-y-temas.md` §3):

```js
parent.postMessage({ tipo: "seccion", seccion: "s2" }, location.origin);
parent.postMessage({ tipo: "elemento", seccion: "s2", titulo: "Ejercicio 4: XOR con NAND",
                     clase: "ejercicio", estado: "resuelto" }, location.origin);
```

`seccion` debe ser una de las del tema en `sitio/temas.json`. Si la lección no envía nada, igual funciona:
las notas quedan por sección.
