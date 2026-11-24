"""Revisa que un HTML de contenido cumpla temas/instrucciones-html.md (P-7, P-31).

    sitio/.venv/bin/python sitio/revisar_html.py temas/alu/practica.html [otro.html ...]

Sale con 0 si todo está bien; si no, lista cada problema. armar_contenido.py usa
la misma revisión y se niega a armar si algún archivo de temas.json no pasa.
No es un analizador completo de HTML: busca, con expresiones regulares, las
fallas que romperían la lección dentro del sitio (scripts de fuera, CDN en el
importmap, módulos que no existen en vendor, pedidos a la red).
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
PREFIJO_VENDOR = "/estaticos/vendor/"
DIR_VENDOR = Path("sitio/web/estaticos/vendor")
FUENTES = ("https://fonts.googleapis.com/",)

RE_SCRIPT = re.compile(r"<script\b([^>]*)>(.*?)</script\s*>", re.S | re.I)
RE_ATRIBUTO = re.compile(r"""\b(src|type)\s*=\s*(?:"([^"]*)"|'([^']*)'|([^\s>]+))""", re.I)
RE_LINK = re.compile(r"<link\b[^>]*>", re.I)
RE_HREF = re.compile(r"""\bhref\s*=\s*(?:"([^"]*)"|'([^']*)'|([^\s>]+))""", re.I)
RE_IMPORT = re.compile(r"""(?:\bfrom\s*|\bimport\s*\(\s*|^\s*import\s+)(["'])([^"']+)\1""", re.M)
RE_RED = re.compile(r"\b(fetch\s*\(|XMLHttpRequest|WebSocket|EventSource|sendBeacon|new\s+Worker\s*\()")


def _atributos(texto: str) -> dict[str, str]:
    return {m.group(1).lower(): next(g for g in m.groups()[1:] if g is not None)
            for m in RE_ATRIBUTO.finditer(texto)}


def _linea(html: str, pos: int) -> int:
    return html.count("\n", 0, pos) + 1


def revisar(html: str, raiz: Path = RAIZ) -> list[str]:
    """Devuelve la lista de problemas (vacía si el archivo cumple)."""
    problemas = []
    vendor = raiz / DIR_VENDOR
    mapa: dict[str, str] = {}

    def existe(ruta: str) -> bool:
        return ruta.startswith(PREFIJO_VENDOR) and (vendor / ruta[len(PREFIJO_VENDOR):]).is_file()

    for m in RE_SCRIPT.finditer(html):
        attrs, cuerpo, n = _atributos(m.group(1)), m.group(2), _linea(html, m.start())
        tipo = attrs.get("type", "").lower()
        if "src" in attrs and not existe(attrs["src"]):
            problemas.append(f"línea {n}: <script src=\"{attrs['src']}\">: solo se permiten scripts de "
                             f"{PREFIJO_VENDOR} que existan en el sitio")
        if tipo == "importmap":
            try:
                imports = json.loads(cuerpo).get("imports", {})
            except ValueError:
                problemas.append(f"línea {n}: el importmap no es JSON válido")
                continue
            for clave, ruta in imports.items():
                ok = existe(ruta) if not ruta.endswith("/") else (
                    ruta.startswith(PREFIJO_VENDOR) and (vendor / ruta[len(PREFIJO_VENDOR):]).is_dir())
                if not ok:
                    problemas.append(f"línea {n}: importmap «{clave}» → «{ruta}»: debe apuntar a "
                                     f"{PREFIJO_VENDOR}three-0.160.0/ (no a un CDN)")
                else:
                    mapa[clave] = ruta
        if tipo == "module":
            for im in RE_IMPORT.finditer(cuerpo):
                esp, ni = im.group(2), _linea(html, m.start(2) + im.start())
                ruta = mapa.get(esp)
                if ruta is None:
                    pref = max((k for k in mapa if k.endswith("/") and esp.startswith(k)), key=len, default=None)
                    ruta = mapa[pref] + esp[len(pref):] if pref else esp
                if not existe(ruta):
                    problemas.append(f"módulo «{esp}» (cerca de la línea {ni}): no existe en el sitio; "
                                     "si es un complemento de Three.js, pide que se agregue a vendor")
        if tipo != "importmap":
            for r in RE_RED.finditer(cuerpo):
                problemas.append(f"línea {_linea(html, m.start(2) + r.start())}: «{r.group(1).strip()}»: "
                                 "el contenido no puede pedir nada a la red")

    for m in RE_LINK.finditer(html):
        tag = m.group(0)
        if not re.search(r"""rel\s*=\s*["']?stylesheet""", tag, re.I):
            continue
        h = RE_HREF.search(tag)
        href = next(g for g in h.groups() if g is not None) if h else ""
        if not href.startswith(FUENTES):
            problemas.append(f"línea {_linea(html, m.start())}: hoja de estilos «{href}»: solo Google Fonts; "
                             "el resto del CSS va en línea")
    return problemas


def main(argv: list[str]) -> int:
    if not argv:
        print(__doc__.strip().splitlines()[2].strip(), file=sys.stderr)
        return 2
    total = 0
    for nombre in argv:
        p = Path(nombre)
        if not p.is_file():
            print(f"{nombre}: no existe")
            total += 1
            continue
        problemas = revisar(p.read_text("utf-8"))
        total += len(problemas)
        print(f"{nombre}: {'bien' if not problemas else f'{len(problemas)} problema(s)'}")
        for x in problemas:
            print(f"  - {x}")
    return 1 if total else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
