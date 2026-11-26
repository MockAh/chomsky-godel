"""Arma la carpeta de contenido a partir de sitio/temas.json (spec 03 §4).

    python sitio/armar_contenido.py [--salida DIR] [--permitir-sucio]

Copia cada archivo declarado como {tema}-{pestana}.html (y su versión en inglés, si
la hay, como {tema}-{pestana}.en.html; P-35), calcula su sha256 y escribe
manifiesto.json (sin las rutas internas `archivo`). Solo lee las fuentes.
Sin --permitir-sucio se niega si algún archivo tiene cambios sin commit.
Siempre se niega si algún HTML no cumple temas/instrucciones-html.md (revisar_html).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

from revisar_html import revisar

RAIZ = Path(__file__).resolve().parent.parent
ID_VALIDO = re.compile(r"^[a-z0-9-]+$")


class ErrorArmado(Exception):
    pass


def _git(raiz: Path, *args: str) -> str:
    r = subprocess.run(["git", *args], cwd=raiz, capture_output=True, text=True)
    if r.returncode != 0:
        raise ErrorArmado(f"git {' '.join(args)} falló: {r.stderr.strip()}")
    return r.stdout


def leer_temas(raiz: Path) -> list[dict]:
    datos = json.loads((raiz / "sitio" / "temas.json").read_text("utf-8"))
    temas = datos["temas"]
    vistos = set()
    for t in temas:
        if not ID_VALIDO.match(t["id"]) or t["id"] in vistos:
            raise ErrorArmado(f"id de tema inválido o repetido: {t['id']!r}")
        vistos.add(t["id"])
        if "grupo" in t and not ID_VALIDO.match(t["grupo"]):
            raise ErrorArmado(f"grupo inválido en {t['id']!r}: {t['grupo']!r}")
        if not t["pestanas"]:
            raise ErrorArmado(f"el tema {t['id']!r} no tiene pestañas")
        ids_p = [p["id"] for p in t["pestanas"]]
        if len(set(ids_p)) != len(ids_p) or not all(ID_VALIDO.match(i) for i in ids_p):
            raise ErrorArmado(f"ids de pestaña inválidos en {t['id']!r}: {ids_p}")
        for s in t.get("secciones", []):
            if not ID_VALIDO.match(s["id"]):
                raise ErrorArmado(f"id de sección inválido en {t['id']!r}: {s['id']!r}")
        en = t.get("en")
        if en is not None and not (isinstance(en, dict) and isinstance(en.get("corto"), str)
                                   and isinstance(en.get("nombre"), str)):
            raise ErrorArmado(f"el bloque «en» del tema {t['id']!r} necesita corto y nombre")
        for p in t["pestanas"]:
            pen = p.get("en")
            if pen is not None and not (isinstance(pen, dict) and isinstance(pen.get("etiqueta"), str)):
                raise ErrorArmado(f"el bloque «en» de {t['id']}/{p['id']} necesita etiqueta")
            for archivo in (p["archivo"], (pen or {}).get("archivo")):
                if archivo is None:
                    continue
                ruta = (raiz / archivo).resolve()
                if not ruta.is_relative_to(raiz) or not ruta.is_file():
                    raise ErrorArmado(f"no existe el archivo {archivo!r}")
    return temas


def archivos_de(temas: list[dict]) -> list[str]:
    """Todos los HTML declarados: el de cada pestaña y, si existe, su versión en inglés."""
    return [a for t in temas for p in t["pestanas"]
            for a in (p["archivo"], (p.get("en") or {}).get("archivo")) if a]


def armar(raiz: Path, salida: Path, permitir_sucio: bool = False) -> dict:
    raiz = raiz.resolve()
    temas = leer_temas(raiz)
    archivos = ["sitio/temas.json"] + archivos_de(temas)
    problemas = [f"{a}: {x}" for a in archivos[1:]
                 for x in revisar((raiz / a).read_text("utf-8"), raiz)]
    if problemas:
        raise ErrorArmado("hay HTML que no cumplen temas/instrucciones-html.md:\n  - "
                          + "\n  - ".join(problemas))
    sucio = bool(_git(raiz, "status", "--porcelain", "--", *archivos).strip())
    if sucio and not permitir_sucio:
        raise ErrorArmado("hay cambios sin commit en el contenido; haz commit o usa --permitir-sucio")
    commit = _git(raiz, "rev-parse", "--short", "HEAD").strip() + ("-sucio" if sucio else "")

    if salida.exists():
        shutil.rmtree(salida)
    salida.mkdir(parents=True)
    manifiesto = {"commit": commit, "temas": []}
    for t in temas:
        pestanas = []
        for p in t["pestanas"]:
            datos = (raiz / p["archivo"]).read_bytes()
            (salida / f"{t['id']}-{p['id']}.html").write_bytes(datos)
            pestana = {
                "id": p["id"], "etiqueta": p["etiqueta"], "anotable": bool(p.get("anotable")),
                "version": p["version"], "sha256": hashlib.sha256(datos).hexdigest(),
                "aviso": p.get("aviso", ""),
            }
            if p.get("en"):
                pen = p["en"]
                pestana["en"] = {"etiqueta": pen["etiqueta"], "aviso": pen.get("aviso", "")}
                if pen.get("archivo"):
                    datos_en = (raiz / pen["archivo"]).read_bytes()
                    (salida / f"{t['id']}-{p['id']}.en.html").write_bytes(datos_en)
                    pestana["en"]["sha256"] = hashlib.sha256(datos_en).hexdigest()
            pestanas.append(pestana)
        tema = {"id": t["id"], "corto": t["corto"], "nombre": t["nombre"],
                "grupo": t.get("grupo", ""),
                "secciones": t.get("secciones", []), "pestanas": pestanas}
        if t.get("en"):
            tema["en"] = {"corto": t["en"]["corto"], "nombre": t["en"]["nombre"]}
        manifiesto["temas"].append(tema)
    (salida / "manifiesto.json").write_text(json.dumps(manifiesto, ensure_ascii=False, indent=1), "utf-8")
    return manifiesto


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--salida", type=Path, default=RAIZ / "sitio" / "contenido")
    ap.add_argument("--permitir-sucio", action="store_true")
    args = ap.parse_args()
    try:
        m = armar(RAIZ, args.salida, args.permitir_sucio)
    except ErrorArmado as e:
        print(f"armar_contenido: {e}", file=sys.stderr)
        return 1
    n = sum(1 + bool(p.get("en", {}).get("sha256")) for t in m["temas"] for p in t["pestanas"])
    print(f"Contenido armado en {args.salida}: {len(m['temas'])} temas, {n} archivos, commit {m['commit']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
