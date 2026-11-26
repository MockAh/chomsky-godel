"""Enlace de solo lectura del sitio, el «museo» (P-34).

    sitio/.venv/bin/python sitio/museo.py abrir https://<url-del-servicio>
    sitio/.venv/bin/python sitio/museo.py cerrar

`abrir` crea una clave nueva (y con eso el enlace anterior deja de servir), guarda
`URL/m/<clave>` en sitio/.museo.txt (permisos 600; no se imprime) y pone en el servicio
solo su huella sha256 como variable MUSEO_HUELLA. `cerrar` quita la variable: todo
/m/... responde 404. Las dos cosas crean una revisión nueva de Cloud Run, así que se
corren con el visto bueno del estudiante. Siempre --project=chomsky-godel (P-26).
"""
from __future__ import annotations

import argparse
import os
import secrets
import subprocess
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))

from invitar import ErrorInvitar, validar_url  # noqa: E402
from servidor import seguridad  # noqa: E402

GCLOUD = ["gcloud", "run", "services", "update", "sitio",
          "--project=chomsky-godel", "--region=us-central1", "--quiet"]
ARCHIVO = AQUI / ".museo.txt"


def nueva_clave() -> tuple[str, str]:
    """Devuelve (clave, huella). La clave va en el enlace; al servicio solo la huella."""
    clave = secrets.token_urlsafe(24)
    return clave, seguridad.huella(clave)


def guardar_enlace(ruta: Path, enlace: str) -> None:
    fd = os.open(ruta, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        f.write(enlace + "\n")
    os.chmod(ruta, 0o600)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="accion", required=True)
    sub.add_parser("abrir").add_argument("url")
    sub.add_parser("cerrar")
    args = ap.parse_args()

    if args.accion == "cerrar":
        r = subprocess.run(GCLOUD + ["--remove-env-vars=MUSEO_HUELLA"])
        if r.returncode == 0:
            ARCHIVO.unlink(missing_ok=True)
            print("museo cerrado: /m/... responde 404")
        return r.returncode

    try:
        url = validar_url(args.url)
    except ErrorInvitar as e:
        print(f"museo: {e}", file=sys.stderr)
        return 1
    clave, huella = nueva_clave()
    r = subprocess.run(GCLOUD + [f"--update-env-vars=MUSEO_HUELLA={huella}"])
    if r.returncode != 0:
        print("museo: gcloud falló; el enlace anterior (si había) sigue igual", file=sys.stderr)
        return r.returncode
    guardar_enlace(ARCHIVO, f"{url}/m/{clave}")
    print("museo abierto; el enlace está en sitio/.museo.txt (los anteriores ya no sirven)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
