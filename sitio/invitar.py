"""Crea las invitaciones de las primeras cuentas en el sitio en línea (spec 04 §6).

    sitio/.venv/bin/python sitio/invitar.py https://<url-del-servicio> [--rol admin|tester]

Lee ADMIN_CORREO y TESTER_CORREO de sitio/.env sin imprimirlos (sin --rol, invita
a cada rol que tenga correo). Usa las credenciales del admin
(`gcloud auth print-access-token`), no una llave de servicio, y siempre el
proyecto chomsky-godel. Escribe `rol: URL/activar#ficha` en sitio/.invitaciones.txt
(permisos 600); en pantalla solo dice qué pasó con cada rol.
"""
from __future__ import annotations

import argparse
import os
import subprocess
import sys
import time
from pathlib import Path
from urllib.parse import urlsplit

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))

from servidor.almacen import CuentaYaActiva  # noqa: E402
from servidor.app import emitir_invitacion  # noqa: E402

PROYECTO = "chomsky-godel"
VARIABLES = {"admin": "ADMIN_CORREO", "tester": "TESTER_CORREO"}


class ErrorInvitar(Exception):
    pass


def leer_env(ruta: Path) -> dict[str, str]:
    if not ruta.is_file():
        return {}
    datos = {}
    for linea in ruta.read_text("utf-8").splitlines():
        linea = linea.strip()
        if linea and not linea.startswith("#") and "=" in linea:
            k, v = linea.split("=", 1)
            datos[k.strip()] = v.strip().strip("'\"")
    return datos


def validar_url(url: str) -> str:
    p = urlsplit(url)
    if p.scheme != "https" or not p.netloc or p.path not in ("", "/") or p.query or p.fragment:
        raise ErrorInvitar("la URL debe ser solo https://<servicio> (sin ruta)")
    return f"https://{p.netloc}"


def escribir_enlaces(ruta: Path, enlaces: dict[str, str]) -> None:
    """Reemplaza las líneas de los roles dados y conserva las demás; permisos 600."""
    lineas = {}
    if ruta.is_file():
        for linea in ruta.read_text("utf-8").splitlines():
            if ": " in linea:
                rol, resto = linea.split(": ", 1)
                lineas[rol] = resto
    lineas.update(enlaces)
    fd = os.open(ruta, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        f.writelines(f"{rol}: {enlace}\n" for rol, enlace in lineas.items())
    os.chmod(ruta, 0o600)


def invitar(almacen, url: str, correos: dict[str, str], roles: list[str], salida: Path,
            ahora: float) -> dict[str, str]:
    """Devuelve, por rol, qué pasó: «invitado», «activa» o «sin correo»."""
    url = validar_url(url)
    estados, enlaces = {}, {}
    for rol in roles:
        correo = correos.get(rol, "")
        if not correo:
            estados[rol] = "sin correo"
            continue
        try:
            ficha = emitir_invitacion(almacen, correo, rol, ahora)
        except CuentaYaActiva:
            estados[rol] = "activa"
            continue
        enlaces[rol] = f"{url}/activar#{ficha}"
        estados[rol] = "invitado"
    if enlaces:
        escribir_enlaces(salida, enlaces)
    return estados


def almacen_en_linea():
    from google.cloud import firestore
    from google.oauth2.credentials import Credentials

    from servidor.almacen_firestore import AlmacenFirestore

    r = subprocess.run(["gcloud", "auth", "print-access-token"], capture_output=True, text=True)
    if r.returncode != 0:
        raise ErrorInvitar("gcloud auth print-access-token falló; ¿sesión de gcloud activa?")
    cliente = firestore.Client(project=PROYECTO, credentials=Credentials(r.stdout.strip()))
    return AlmacenFirestore(cliente)


MENSAJES = {
    "invitado": "invitación creada (14 días); enlace en sitio/.invitaciones.txt",
    "activa": "la cuenta ya está activa; sin enlace",
    "sin correo": "sin correo en sitio/.env; no se invitó",
}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("url")
    ap.add_argument("--rol", choices=sorted(VARIABLES))
    args = ap.parse_args()
    env = leer_env(AQUI / ".env")
    correos = {rol: env.get(var, "") for rol, var in VARIABLES.items()}
    roles = [args.rol] if args.rol else [r for r in VARIABLES if correos[r]]
    if not roles:
        print("invitar: no hay ADMIN_CORREO ni TESTER_CORREO en sitio/.env", file=sys.stderr)
        return 1
    try:
        validar_url(args.url)
        estados = invitar(almacen_en_linea(), args.url, correos, roles,
                          AQUI / ".invitaciones.txt", time.time())
    except ErrorInvitar as e:
        print(f"invitar: {e}", file=sys.stderr)
        return 1
    for rol, estado in estados.items():
        print(f"  {rol}: {MENSAJES[estado]}")
    return 0 if all(e != "sin correo" for e in estados.values()) else 1


if __name__ == "__main__":
    sys.exit(main())
