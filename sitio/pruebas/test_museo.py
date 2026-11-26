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


# ---------- inglés (P-35) ----------

@pytest.fixture
def museo_en(contenido, reloj):
    import json
    m = json.loads((contenido / "manifiesto.json").read_text("utf-8"))
    logica = m["temas"][0]
    logica["en"] = {"corto": "Logic", "nombre": "Boolean logic"}
    logica["pestanas"][0]["en"] = {"etiqueta": "Practice", "aviso": "", "sha256": "e1"}
    logica["pestanas"][1]["en"] = {"etiqueta": "Map", "aviso": "Under review"}
    (contenido / "manifiesto.json").write_text(json.dumps(m), "utf-8")
    (contenido / "logica-practica.en.html").write_text("<p>practice in English</p>", "utf-8")
    app = crear_app(AlmacenProhibido(), contenido, reloj=reloj, huella_museo=seguridad.huella(CLAVE))
    return nuevo_cliente(app)


@pytest.mark.parametrize("ruta", RUTAS)
def test_ingles_responde(museo_en, ruta):
    assert museo_en.get(f"/m/{CLAVE}/en{ruta}").status_code == 200
    assert museo_en.get(f"/m/otra/en{ruta}").status_code == 404


def test_ingles_nombres_y_solo_es(museo_en):
    temas = museo_en.get(f"/m/{CLAVE}/en/api/temas").json()["temas"]
    logica, alu = temas[0], temas[1]
    assert (logica["corto"], logica["nombre"]) == ("Logic", "Boolean logic")
    assert [(p["etiqueta"], p["aviso"], p["solo_es"]) for p in logica["pestanas"]] == [
        ("Practice", "", False), ("Map", "Under review", True)]
    assert alu["nombre"] == "Unidad aritmético-lógica" and alu["pestanas"][0]["solo_es"]
    es = museo_en.get(f"/m/{CLAVE}/api/temas").json()["temas"]
    assert es[0]["nombre"] == "Lógica booleana" and not es[0]["pestanas"][1]["solo_es"]


def test_ingles_contenido_con_respaldo_en_espanol(museo_en, contenido):
    assert museo_en.get(f"/m/{CLAVE}/en/contenido/logica/practica").text == "<p>practice in English</p>"
    assert museo_en.get(f"/m/{CLAVE}/contenido/logica/practica").text == \
        (contenido / "logica-practica.html").read_text("utf-8")
    r = museo_en.get(f"/m/{CLAVE}/en/contenido/logica/mapa")
    assert r.text == (contenido / "logica-mapa.html").read_text("utf-8")
    assert r.headers["content-security-policy"] == CSP_CONTENIDO
