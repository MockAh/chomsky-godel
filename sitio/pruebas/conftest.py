import json
import os
import shutil
import socket
import subprocess
import time

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
        {"id": "fase-1", "corto": "Fase 1", "nombre": "La máquina desnuda", "grupo": "claude",
         "secciones": [{"id": "mt1", "nombre": "Mini-tarea 1"}],
         "pestanas": [{"id": "leccion", "etiqueta": "Lección", "anotable": True,
                       "version": "v0.1", "sha256": "h4", "aviso": ""}]},
    ]}
    (d / "manifiesto.json").write_text(json.dumps(manifiesto), "utf-8")
    for nombre in ("logica-practica", "logica-mapa", "alu-practica", "fase-1-leccion"):
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


# ---------- emulador de Firestore (F4) ----------

PUERTO_EMULADOR = 8085


def _escucha(host, puerto):
    try:
        with socket.create_connection((host, puerto), timeout=0.5):
            return True
    except OSError:
        return False


@pytest.fixture(scope="session")
def emulador():
    """Cliente de Firestore contra el emulador.

    Usa FIRESTORE_EMULATOR_HOST si ya hay uno corriendo; si no, lo levanta con
    `gcloud emulators firestore start` y lo apaga al final. Sin Java o sin el
    componente del emulador, las pruebas de Firestore se saltan con el motivo.
    """
    proceso = None
    if not os.environ.get("FIRESTORE_EMULATOR_HOST"):
        if not shutil.which("gcloud") or not shutil.which("java"):
            pytest.skip("emulador de Firestore no disponible: falta gcloud o java")
        proceso = subprocess.Popen(
            ["gcloud", "emulators", "firestore", "start", f"--host-port=127.0.0.1:{PUERTO_EMULADOR}"],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
        limite = time.time() + 60
        while not _escucha("127.0.0.1", PUERTO_EMULADOR):
            if proceso.poll() is not None or time.time() > limite:
                proceso.kill()
                pytest.skip("el emulador de Firestore no arrancó (¿falta el componente?)")
            time.sleep(0.5)
        os.environ["FIRESTORE_EMULATOR_HOST"] = f"127.0.0.1:{PUERTO_EMULADOR}"
    from google.cloud import firestore
    yield firestore.Client(project="chomsky-godel-pruebas")
    if proceso:
        os.killpg(proceso.pid, 15)
        proceso.wait(timeout=10)
        del os.environ["FIRESTORE_EMULATOR_HOST"]
