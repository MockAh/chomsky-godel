"""invitar.py (spec 04 §6) con AlmacenMemoria."""
import stat

import pytest

from invitar import ErrorInvitar, invitar, leer_env
from servidor import seguridad
from servidor.almacen import AlmacenMemoria

URL = "https://sitio-1.us-central1.run.app"
AHORA = 1_800_000_000.0


def test_invita_solo_admin_y_guarda_enlace_privado(tmp_path):
    almacen, salida = AlmacenMemoria(), tmp_path / ".invitaciones.txt"
    correos = {"admin": "Admin@Ejemplo.org", "tester": "t@ejemplo.org"}
    estados = invitar(almacen, URL + "/", correos, ["admin"], salida, AHORA)
    assert estados == {"admin": "invitado"}
    texto = salida.read_text("utf-8")
    assert texto.startswith(f"admin: {URL}/activar#") and "tester" not in texto
    assert stat.S_IMODE(salida.stat().st_mode) == 0o600
    ficha = texto.strip().split("#", 1)[1]
    inv = almacen.obtener_invitacion(seguridad.huella(ficha), AHORA)
    assert inv and inv["rol"] == "admin" and inv["correo"] == "admin@ejemplo.org"
    assert ficha not in str(almacen.__dict__)  # en la base solo va la huella


def test_cuenta_activa_no_recibe_enlace(tmp_path):
    almacen, salida = AlmacenMemoria(), tmp_path / ".invitaciones.txt"
    almacen.guardar_usuario("admin@ejemplo.org", "hash", "admin")
    estados = invitar(almacen, URL, {"admin": "admin@ejemplo.org"}, ["admin"], salida, AHORA)
    assert estados == {"admin": "activa"} and not salida.exists()


def test_sin_correo_y_conserva_otras_lineas(tmp_path):
    almacen, salida = AlmacenMemoria(), tmp_path / ".invitaciones.txt"
    invitar(almacen, URL, {"admin": "a@ejemplo.org"}, ["admin"], salida, AHORA)
    antes = salida.read_text("utf-8")
    estados = invitar(almacen, URL, {"admin": "a@ejemplo.org"}, ["tester"], salida, AHORA)
    assert estados == {"tester": "sin correo"} and salida.read_text("utf-8") == antes


@pytest.mark.parametrize("mala", ["http://x.run.app", "https://x.run.app/activar", "x.run.app"])
def test_url_invalida(tmp_path, mala):
    with pytest.raises(ErrorInvitar):
        invitar(AlmacenMemoria(), mala, {"admin": "a@e.org"}, ["admin"], tmp_path / "s", AHORA)


def test_leer_env(tmp_path):
    env = tmp_path / ".env"
    env.write_text("# c\nADMIN_CORREO = 'a@e.org'\nTESTER_CORREO=\n", "utf-8")
    assert leer_env(env) == {"ADMIN_CORREO": "a@e.org", "TESTER_CORREO": ""}
    assert leer_env(tmp_path / "no") == {}
