import json

import pytest
from fastapi.testclient import TestClient

from servidor import seguridad
from servidor.almacen import AlmacenMemoria
from servidor.app import crear_app

ORIGEN = "https://testserver"
CONTRASENA = "Correcta-Larga-1"
ADMIN = "admin@ejemplo.org"
TESTER = "tester@ejemplo.org"


class RelojFalso:
    def __init__(self, t=1_800_000_000.0):
        self.t = t

    def __call__(self):
        return self.t

    def avanzar(self, segundos):
        self.t += segundos


@pytest.fixture
def contenido(tmp_path):
    d = tmp_path / "contenido"
    d.mkdir()
    manifiesto = {"commit": "abc1234", "temas": [
        {"id": "logica", "corto": "Lógica", "nombre": "Lógica booleana",
         "secciones": [{"id": "s1", "nombre": "Álgebra"}, {"id": "s2", "nombre": "Compuertas"}],
         "pestanas": [
             {"id": "practica", "etiqueta": "Práctica", "anotable": True, "version": "v0.1",
              "sha256": "h1", "aviso": ""},
             {"id": "mapa", "etiqueta": "Mapa", "anotable": False, "version": "v0.1",
              "sha256": "h2", "aviso": "En revisión"}]},
        {"id": "alu", "corto": "ALU", "nombre": "Unidad aritmético-lógica", "secciones": [],
         "pestanas": [{"id": "practica", "etiqueta": "Práctica", "anotable": True,
                       "version": "v0.1", "sha256": "h3", "aviso": ""}]},
    ]}
    (d / "manifiesto.json").write_text(json.dumps(manifiesto), "utf-8")
    for nombre in ("logica-practica", "logica-mapa", "alu-practica"):
        (d / f"{nombre}.html").write_text(f"<!doctype html><p>{nombre}</p>", "utf-8")
    return d


@pytest.fixture
def reloj():
    return RelojFalso()


@pytest.fixture
def almacen():
    a = AlmacenMemoria()
    a.guardar_usuario(ADMIN, seguridad.hashear(CONTRASENA), "admin")
    a.guardar_usuario(TESTER, seguridad.hashear(CONTRASENA), "tester")
    return a


@pytest.fixture
def app(almacen, contenido, reloj):
    return crear_app(almacen, contenido, reloj=reloj)


def nuevo_cliente(app, origen=ORIGEN):
    headers = {"Origin": origen} if origen else {}
    return TestClient(app, base_url=ORIGEN, headers=headers, follow_redirects=False)


@pytest.fixture
def cliente(app):
    return nuevo_cliente(app)


def entrar(c, correo=TESTER, contrasena=CONTRASENA):
    return c.post("/api/login", json={"correo": correo, "contrasena": contrasena})
