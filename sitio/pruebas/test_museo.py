"""Museo: enlace de solo lectura /m/<clave>/… (P-34)."""
import pytest

from conftest import nuevo_cliente
from servidor import seguridad
from servidor.app import CSP_CONTENIDO, crear_app

CLAVE = "clave-del-museo-de-prueba-0123456789"


class AlmacenProhibido:
    """El museo no debe tocar la base: cualquier uso del almacén falla."""

    def __getattr__(self, nombre):
        raise AssertionError(f"el museo usó el almacén: {nombre}")


@pytest.fixture
def museo(contenido, reloj):
    app = crear_app(AlmacenProhibido(), contenido, reloj=reloj, huella_museo=seguridad.huella(CLAVE))
    return nuevo_cliente(app)


RUTAS = ["", "/temas", "/t/logica", "/contenido/logica/practica", "/api/temas"]


@pytest.mark.parametrize("ruta", RUTAS)
def test_con_clave_se_ve_sin_sesion_ni_cookies(museo, ruta):
    r = museo.get(f"/m/{CLAVE}{ruta}")
    assert r.status_code == 200
    assert "set-cookie" not in r.headers
    assert r.headers["x-robots-tag"] == "noindex, nofollow"


def test_paginas_y_contenido(museo, contenido):
    assert "credenciales" in museo.get(f"/m/{CLAVE}").text  # la misma esfera de entrada
    r = museo.get(f"/m/{CLAVE}/contenido/logica/mapa")
    assert r.text == (contenido / "logica-mapa.html").read_text("utf-8")
    assert r.headers["content-security-policy"] == CSP_CONTENIDO


def test_api_temas_sin_huellas_y_nada_anotable(museo):
    temas = museo.get(f"/m/{CLAVE}/api/temas").json()["temas"]
    assert [t["id"] for t in temas] == ["logica", "alu", "fase-1"]
    pestanas = [p for t in temas for p in t["pestanas"]]
    assert all(not p["anotable"] and "sha256" not in p for p in pestanas)
    assert "secciones" not in temas[0]


@pytest.mark.parametrize("ruta", RUTAS)
@pytest.mark.parametrize("clave", ["otra-clave", CLAVE + "x", "x" * 200])
def test_clave_equivocada_es_404(museo, ruta, clave):
    r = museo.get(f"/m/{clave}{ruta}")
    assert r.status_code == 404


@pytest.mark.parametrize("ruta", ["/t/nada", "/contenido/logica/nada", "/contenido/nada/practica"])
def test_lo_que_no_existe_es_404(museo, ruta):
    assert museo.get(f"/m/{CLAVE}{ruta}").status_code == 404


@pytest.mark.parametrize("huella", [None, "", "no-es-hex", "A" * 64])
def test_sin_huella_valida_el_museo_esta_cerrado(contenido, reloj, huella):
    c = nuevo_cliente(crear_app(AlmacenProhibido(), contenido, reloj=reloj, huella_museo=huella))
    for ruta in RUTAS:
        assert c.get(f"/m/{CLAVE}{ruta}").status_code == 404


@pytest.mark.parametrize("metodo", ["post", "put", "delete", "patch"])
def test_solo_lectura(museo, metodo):
    r = museo.request(metodo.upper(), f"/m/{CLAVE}/api/temas", json={})
    assert r.status_code == 405


def test_la_clave_no_abre_el_sitio_privado(almacen, contenido, reloj):
    c = nuevo_cliente(crear_app(almacen, contenido, reloj=reloj, huella_museo=seguridad.huella(CLAVE)))
    c.get(f"/m/{CLAVE}/temas")
    assert c.get("/api/sesion").status_code == 401
    assert c.get("/api/anotaciones/logica").status_code == 401
    assert c.get("/contenido/logica/practica").status_code == 401
    assert c.put("/api/anotaciones/logica/practica/s1", json={"texto": "x"}).status_code == 401
    assert c.get("/").status_code == 302
