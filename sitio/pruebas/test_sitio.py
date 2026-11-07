"""Páginas, contenido, encabezados y manifiesto (spec 05 §1). Anotaciones: F3."""
from conftest import entrar
from servidor.app import CSP_CONTENIDO, CSP_SITIO, ENCABEZADOS


def test_tema_o_pestana_inexistentes(cliente):
    entrar(cliente)
    assert cliente.get("/t/nada").status_code == 404
    assert cliente.get("/t/logica").status_code == 200
    assert cliente.get("/contenido/logica/nada").status_code == 404
    assert cliente.get("/contenido/nada/practica").status_code == 404
    assert cliente.get("/contenido/..%2Fsecreto/practica").status_code == 404


def test_csp_del_contenido_y_del_sitio(cliente):
    entrar(cliente)
    r = cliente.get("/contenido/logica/practica")
    assert r.status_code == 200 and "logica-practica" in r.text
    assert r.headers["content-security-policy"] == CSP_CONTENIDO
    for ruta in ("/login", "/", "/api/sesion", "/estaticos/favicon.svg", "/salud", "/t/nada"):
        r = cliente.get(ruta)
        assert r.headers["content-security-policy"] == CSP_SITIO, ruta
        for k, v in ENCABEZADOS.items():
            assert r.headers[k] == v, (ruta, k)


def test_sesion_devuelve_temas_en_orden_y_sin_rutas(cliente):
    entrar(cliente)
    temas = cliente.get("/api/sesion").json()["temas"]
    assert [t["id"] for t in temas] == ["logica", "alu"]
    assert temas[1]["secciones"] == [{"id": "general", "nombre": "General"}]
    assert "archivo" not in str(temas)
    assert temas[0]["pestanas"][1]["aviso"] == "En revisión"


def test_sin_documentacion_automatica(cliente):
    for ruta in ("/docs", "/redoc", "/openapi.json"):
        assert cliente.get(ruta).status_code == 404


def test_salud(cliente):
    assert cliente.get("/salud").status_code == 204


def test_paginas_solo_cargan_recursos_propios(cliente):
    """La CSP del sitio no permite scripts ni estilos en línea ni de otros dominios."""
    import re
    from servidor.app import DIR_WEB
    for pagina in DIR_WEB.glob("*.html"):
        html = pagina.read_text("utf-8")
        assert not re.search(r"<script(?![^>]*\bsrc=)[^>]*>", html), pagina.name
        assert "<style" not in html and " style=" not in html, pagina.name
        for url in re.findall(r'(?:src|href)="([^"]+)"', html):
            assert url.startswith("/"), (pagina.name, url)
            if url.startswith("/estaticos/"):
                assert cliente.get(url).status_code == 200, url
