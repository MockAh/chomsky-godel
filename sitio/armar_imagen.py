"""Arma la carpeta exacta que sube a Cloud Build (spec 04 §4).

    python sitio/armar_imagen.py [SALIDA] [--permitir-sucio]

Lista cerrada: servidor/, web/, Dockerfile, cloudbuild.yaml, requirements.txt y
contenido/ (armado con armar_contenido). Nada más: ni .env, ni .venv, ni pruebas,
ni el resto del repositorio. Sin --permitir-sucio se niega si sitio/ o el
contenido tienen cambios sin commit.
"""
from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

from armar_contenido import RAIZ, ErrorArmado, _git, armar

# (origen relativo a sitio/, destino dentro de la imagen)
LISTA_CERRADA = [
    ("servidor", "servidor"),
    ("web", "web"),
    ("despliegue/Dockerfile", "Dockerfile"),
    ("despliegue/cloudbuild.yaml", "cloudbuild.yaml"),
    ("requirements.txt", "requirements.txt"),
]
IGNORAR = shutil.ignore_patterns("__pycache__", "*.pyc", ".*")


def armar_imagen(raiz: Path, salida: Path, permitir_sucio: bool = False) -> dict:
    raiz = raiz.resolve()
    salida = salida.resolve()
    if salida == raiz or raiz.is_relative_to(salida) or salida.is_relative_to(raiz / "sitio"):
        raise ErrorArmado(f"salida peligrosa: {salida}")
    sucio = bool(_git(raiz, "status", "--porcelain", "--", "sitio").strip())
    if sucio and not permitir_sucio:
        raise ErrorArmado("hay cambios sin commit en sitio/; haz commit o usa --permitir-sucio")

    if salida.exists():
        shutil.rmtree(salida)
    salida.mkdir(parents=True)
    sitio = raiz / "sitio"
    for origen, destino in LISTA_CERRADA:
        o = sitio / origen
        if o.is_dir():
            shutil.copytree(o, salida / destino, ignore=IGNORAR)
        elif o.is_file():
            shutil.copy2(o, salida / destino)
        else:
            raise ErrorArmado(f"falta sitio/{origen}")
    m = armar(raiz, salida / "contenido", permitir_sucio)
    if sucio and not m["commit"].endswith("-sucio"):
        m["commit"] += "-sucio"
    return m


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("salida", type=Path, nargs="?", default=RAIZ / "build" / "sitio-imagen")
    ap.add_argument("--permitir-sucio", action="store_true")
    args = ap.parse_args()
    try:
        m = armar_imagen(RAIZ, args.salida, args.permitir_sucio)
    except ErrorArmado as e:
        print(f"armar_imagen: {e}", file=sys.stderr)
        return 1
    print(f"Imagen armada en {args.salida}: commit {m['commit']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
