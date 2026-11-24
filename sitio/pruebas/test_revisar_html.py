"""revisar_html (temas/instrucciones-html.md, P-31)."""
import json

import pytest

from armar_contenido import RAIZ
from revisar_html import revisar

MAPA = """<script type="importmap">{ "imports": {
  "three": "/estaticos/vendor/three-0.160.0/three.module.min.js",
  "three/addons/": "/estaticos/vendor/three-0.160.0/addons/" } }</script>"""
FUENTE = '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=X">'


def test_leccion_3d_correcta_pasa():
    html = FUENTE + MAPA + """<script type="module">
import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
</script><p>fetch-decode-execute</p>"""
    assert revisar(html, RAIZ) == []


@pytest.mark.parametrize("html, pista", [
    ('<script src="https://cdn.jsdelivr.net/npm/three"></script>', "<script src"),
    ('<script type="importmap">{"imports": {"three": "https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.module.js"}}</script>',
     "importmap"),
    (MAPA + '<script type="module">import { X } from "three/addons/nada/X.js";</script>', "pide que se agregue"),
    ('<script type="module">import * as THREE from "three";</script>', "no existe"),
    ('<script>fetch("/api/sesion")</script>', "red"),
    ('<script>const ws = new WebSocket("wss://x")</script>', "red"),
    ('<link rel="stylesheet" href="https://cdn.ejemplo.com/a.css">', "Google Fonts"),
    ('<script type="importmap">{no es json</script>', "JSON"),
])
def test_detecta_problemas(html, pista):
    problemas = revisar(html, RAIZ)
    assert problemas and any(pista in p for p in problemas), problemas


def test_todas_las_lecciones_publicadas_cumplen():
    temas = json.loads((RAIZ / "sitio" / "temas.json").read_text("utf-8"))["temas"]
    for t in temas:
        for p in t["pestanas"]:
            assert revisar((RAIZ / p["archivo"]).read_text("utf-8"), RAIZ) == [], p["archivo"]

