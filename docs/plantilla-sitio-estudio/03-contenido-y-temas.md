# 03 · Contenido y temas

## 1. Manifiesto fuente: `sitio/temas.json`

Es la **lista cerrada** de lo que se publica: solo lo que esté aquí llega a la nube. El orden es el de la
pantalla «Elige un tema».

```json
{
  "_nota": "Lista cerrada de lo que sube al sitio. Publicar es desplegar.",
  "temas": [
    {
      "id": "logica-booleana",
      "corto": "Lógica booleana",
      "nombre": "Lógica booleana y circuitos lógicos",
      "secciones": [
        {"id": "s1", "nombre": "Álgebra de Boole"},
        {"id": "s2", "nombre": "Compuertas"},
        {"id": "s3", "nombre": "Circuitos combinacionales"}
      ],
      "pestanas": [
        {"id": "practica", "etiqueta": "Práctica", "anotable": true,
         "archivo": "temas/logica-booleana/practica.html", "version": "v0.1"},
        {"id": "mapa", "etiqueta": "Mapa", "anotable": false,
         "archivo": "temas/logica-booleana/mapa.html", "version": "v0.1", "aviso": "En revisión"}
      ]
    },
    {"id": "alu", "corto": "ALU", "nombre": "Unidad aritmético-lógica", "secciones": [], "pestanas": []},
    {"id": "cpu", "corto": "CPU", "nombre": "La CPU a alto nivel", "secciones": [], "pestanas": []}
  ]
}
```

Reglas:
- `id` de tema y de pestaña: `[a-z0-9-]+`. Son parte de la URL.
- Cada tema tiene **al menos una** pestaña antes de publicarse (las listas vacías del ejemplo son de relleno).
- `grupo` (opcional, `[a-z0-9-]+`): agrupa temas en la pantalla de inicio. Con `"claude"`, el tema va en
  la sección «Lecciones de Claude» (una por fase, P-24); sin él, en la lista de siempre.
- `secciones` son las casillas fijas de anotaciones del tema. Si un tema no las
  tiene, se usa una sola sección implícita `general`.
- Para agregar un tema: crear `temas/{id}/…html`, añadirlo aquí, hacer commit y desplegar. No se toca el código.

Fuentes del contenido sugeridas en el repositorio nuevo:
```
temas/
  cpu/          practica.html  mapa.html
  alu/          practica.html  mapa.html
  logica-booleana/ practica.html  mapa.html
```

## 2. Contrato de los HTML de contenido

Cada pestaña es **un solo archivo HTML autocontenido**:

- Scripts y estilos **en línea**. Imágenes como `data:` URI (o SVG en línea).
- Puede usar Google Fonts. **No** puede cargar scripts de otros sitios ni hacer `fetch` a ningún lado.
- Si un simulador necesita una biblioteca (ej. para dibujar circuitos), se **incrusta** en el archivo.
- No usa `localStorage` para nada importante: el iframe comparte origen con el sitio.

El servidor lo entrega con esta CSP:
```
default-src 'none'; script-src 'unsafe-inline'; style-src 'unsafe-inline' https://fonts.googleapis.com;
font-src https://fonts.gstatic.com; img-src data: blob:; base-uri 'none'; form-action 'none';
frame-ancestors 'self'
```
(`blob:` en imágenes permite que los simuladores exporten dibujos de `<canvas>`.) Si un tema necesita más, se cambia aquí y se anota como decisión.

**Por qué mismo origen y no `sandbox`:** la página de tema necesita poner la etiqueta de aviso dentro del
contenido y escuchar los mensajes de §3. Con `postMessage` (§3) bastaría un iframe aislado; si se quiere
aislar del todo, se agrega `sandbox="allow-scripts"` al `<iframe>` y se quita la etiqueta en línea. Decisión
abierta (**P-1**).

## 3. Anotaciones por elemento: contrato explícito

El sitio **no lee el DOM de la lección** para adivinar en qué ejercicio va el estudiante: eso ata el sitio a
cómo esté hecha cada lección. En su lugar, la lección avisa al sitio con `postMessage`:

```js
// Dentro del HTML del tema, cuando el estudiante entra a una sección o termina un elemento:
parent.postMessage({ tipo: "seccion", seccion: "s2" }, location.origin);
parent.postMessage({ tipo: "elemento", seccion: "s2",
                     titulo: "Ejercicio 4: XOR con NAND",
                     clase: "ejercicio",          // ejercicio | circuito | pregunta | lectura
                     estado: "resuelto" }, location.origin);
```

El sitio (`tema.js`):
- Acepta solo mensajes con `event.origin === location.origin` y `event.source` = el iframe anotable.
- Con `seccion`: abre la vista de anotaciones en esa sección.
- Con `elemento`: muestra un botón flotante «Anotar este ejercicio», que abre un diálogo con su casilla.
- Valida `seccion` contra `temas.json` y la longitud de cada campo (igual que el servidor).

Un contenido que no envía mensajes sigue funcionando: solo tendrá las casillas por sección.

## 4. Armado del contenido: `armar_contenido.py`

Entrada: `temas.json`. Salida: una carpeta `contenido/` que va dentro de la imagen.

1. Sin `--permitir-sucio`, se niega si algún archivo enlistado tiene cambios sin commit
   (`git status --porcelain -- <archivos>`). Así cada despliegue es rastreable.
2. Copia cada archivo como `contenido/{tema}-{pestana}.html`. **Solo lee** las fuentes; no las modifica.
3. Calcula `sha256` de cada uno.
4. Escribe `contenido/manifiesto.json`:
   ```json
   {"commit": "a1b2c3d", "temas": [{"id": "...", "corto": "...", "nombre": "...", "secciones": [...],
     "pestanas": [{"id": "practica", "etiqueta": "Práctica", "anotable": true,
                   "version": "v0.1", "sha256": "…", "aviso": ""}]}]}
   ```
   (sin la ruta interna `archivo`).

El servidor carga ese manifiesto al arrancar; de ahí salen los temas válidos, las pestañas y las secciones.

## 5. Versiones y notas

- Cada nota guarda `version` (la etiqueta humana) y `version_hash` (el sha256 del archivo publicado).
- Al publicar un archivo distinto, las notas viejas no se pierden: pasan a «anteriores», con su versión.
- Cambiar solo la etiqueta `version` sin cambiar el archivo **no** reinicia las notas; cambiar el archivo sí,
  aunque la etiqueta no cambie.

## 6. Módulo opcional: biblioteca de lecturas

Si después se quieren servir lecturas (PDF, apuntes) dentro del sitio: un `documentos.json` con `clave, archivo, tipo, enlace_oficial`, copiado por
`armar_contenido.py`, rutas `/documentos/...` con sesión, y los HTML de terceros servidos con
`Content-Security-Policy: sandbox; default-src 'none'`. Solo materiales cuya licencia permita volver a
servirlos; si no, solo el enlace.
