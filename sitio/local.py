"""Levanta el sitio en http://localhost:8080 con AlmacenMemoria (spec 04 §7).

    sitio/.venv/bin/python sitio/local.py [--puerto 8080]

Arma el contenido con --permitir-sucio, crea una cuenta admin con contraseña
aleatoria y un enlace de activación para el tester. Todo se pierde al apagar.
Abre siempre http://localhost:8080 (no 127.0.0.1): la cookie es Secure y los
navegadores solo la aceptan sin HTTPS en «localhost».
"""
from __future__ import annotations

import argparse
import secrets
import sys
import time
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))

import uvicorn  # noqa: E402

from armar_contenido import RAIZ, ErrorArmado, armar  # noqa: E402
from servidor import seguridad  # noqa: E402
from servidor.almacen import AlmacenMemoria  # noqa: E402
from servidor.app import crear_app, emitir_invitacion  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser(description="Sitio en local con almacén en memoria.")
    ap.add_argument("--puerto", type=int, default=8080)
    puerto = ap.parse_args().puerto
    url = f"http://localhost:{puerto}"
    try:
        m = armar(RAIZ, AQUI / "contenido", permitir_sucio=True)
    except ErrorArmado as e:
        print(f"No se pudo armar el contenido: {e}", file=sys.stderr)
        return 1

    almacen = AlmacenMemoria()
    admin, tester = "admin@local", "tester@local"
    contrasena = secrets.token_urlsafe(9) + "-Aa1"
    almacen.guardar_usuario(admin, seguridad.hashear(contrasena), "admin")
    ficha = emitir_invitacion(almacen, tester, "tester", time.time())

    print(f"\n  chomsky-godel en local · contenido {m['commit']}\n")
    print(f"  {url}")
    print(f"  admin:  {admin}  /  {contrasena}")
    print(f"  tester: {url}/activar#{ficha}  (crea su contraseña; correo {tester})\n", flush=True)

    app = crear_app(almacen, AQUI / "contenido")
    uvicorn.run(app, host="127.0.0.1", port=puerto, log_level="warning",
                server_header=False, access_log=False)
    return 0


if __name__ == "__main__":
    sys.exit(main())
