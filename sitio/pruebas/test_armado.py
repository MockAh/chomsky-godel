"""armar_contenido y armar_imagen (spec 05 §1, 04 §4)."""
import json
import subprocess

import pytest

from armar_contenido import ErrorArmado, armar
from armar_imagen import armar_imagen


def git(raiz, *args):
    subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t", *args], cwd=raiz,
                   check=True, capture_output=True)


@pytest.fixture
def repo(tmp_path):
    (tmp_path / "sitio").mkdir()
    (tmp_path / "temas" / "a").mkdir(parents=True)
    (tmp_path / "temas" / "a" / "p.html").write_text("<p>hola</p>", "utf-8")
    (tmp_path / "sitio" / "temas.json").write_text(json.dumps({"temas": [
        {"id": "a", "corto": "A", "nombre": "Tema A", "secciones": [],
         "pestanas": [{"id": "p", "etiqueta": "Práctica", "anotable": True,
                       "archivo": "temas/a/p.html", "version": "v0.1"}]}]}), "utf-8")
    git(tmp_path, "init", "-q")
    git(tmp_path, "add", "-A")
    git(tmp_path, "commit", "-q", "-m", "inicio")
    return tmp_path


def test_arma_limpio(repo):
    m = armar(repo, repo / "salida")
    assert not m["commit"].endswith("-sucio")
    p = m["temas"][0]["pestanas"][0]
    assert "archivo" not in p and len(p["sha256"]) == 64
    assert (repo / "salida" / "a-p.html").read_text("utf-8") == "<p>hola</p>"
    assert json.loads((repo / "salida" / "manifiesto.json").read_text("utf-8")) == m


def test_se_niega_con_cambios_sin_commit(repo):
    (repo / "temas" / "a" / "p.html").write_text("<p>cambio</p>", "utf-8")
    with pytest.raises(ErrorArmado):
        armar(repo, repo / "salida")
    m = armar(repo, repo / "salida", permitir_sucio=True)
    assert m["commit"].endswith("-sucio")
    assert (repo / "temas" / "a" / "p.html").read_text("utf-8") == "<p>cambio</p>"  # solo lee


def test_se_niega_si_falta_archivo_o_pestanas(repo):
    datos = json.loads((repo / "sitio" / "temas.json").read_text("utf-8"))
    datos["temas"][0]["pestanas"][0]["archivo"] = "temas/a/no-existe.html"
    (repo / "sitio" / "temas.json").write_text(json.dumps(datos), "utf-8")
    with pytest.raises(ErrorArmado):
        armar(repo, repo / "salida", permitir_sucio=True)
    datos["temas"][0]["pestanas"] = []
    (repo / "sitio" / "temas.json").write_text(json.dumps(datos), "utf-8")
    with pytest.raises(ErrorArmado):
        armar(repo, repo / "salida", permitir_sucio=True)


def test_grupo_se_copia_y_se_valida(repo):
    m = armar(repo, repo / "salida")
    assert m["temas"][0]["grupo"] == ""
    datos = json.loads((repo / "sitio" / "temas.json").read_text("utf-8"))
    datos["temas"][0]["grupo"] = "claude"
    (repo / "sitio" / "temas.json").write_text(json.dumps(datos), "utf-8")
    assert armar(repo, repo / "salida", permitir_sucio=True)["temas"][0]["grupo"] == "claude"
    datos["temas"][0]["grupo"] = "Claude!"
    (repo / "sitio" / "temas.json").write_text(json.dumps(datos), "utf-8")
    with pytest.raises(ErrorArmado):
        armar(repo, repo / "salida", permitir_sucio=True)


def test_armar_se_niega_con_html_que_no_cumple(repo):
    (repo / "temas" / "a" / "p.html").write_text('<script src="https://cdn.x/y.js"></script>', "utf-8")
    with pytest.raises(ErrorArmado, match="instrucciones-html"):
        armar(repo, repo / "salida", permitir_sucio=True)


@pytest.fixture
def repo_sitio(repo):
    s = repo / "sitio"
    for d in ("servidor", "web/estaticos", "despliegue", "pruebas", ".venv/bin"):
        (s / d).mkdir(parents=True)
    (s / "servidor" / "app.py").write_text("x = 1\n", "utf-8")
    (s / "web" / "login.html").write_text("<p>login</p>", "utf-8")
    (s / "web" / "estaticos" / "base.css").write_text("body{}", "utf-8")
    (s / "despliegue" / "Dockerfile").write_text("FROM python:3.12-slim\n", "utf-8")
    (s / "despliegue" / "cloudbuild.yaml").write_text("steps: []\n", "utf-8")
    (s / "despliegue" / "preparar-proyecto.sh").write_text("#!/bin/sh\n", "utf-8")
    (s / "requirements.txt").write_text("fastapi\n", "utf-8")
    (s / "pruebas" / "test_x.py").write_text("", "utf-8")
    (s / ".gitignore").write_text(".env\n.invitaciones.txt\n.venv/\n__pycache__/\n", "utf-8")
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "sitio")
    (s / ".env").write_text("ADMIN_CORREO=secreto@ejemplo.org\n", "utf-8")
    (s / ".invitaciones.txt").write_text("admin: https://x/activar#ficha\n", "utf-8")
    (s / ".venv" / "bin" / "python").write_text("", "utf-8")
    (s / "servidor" / "__pycache__").mkdir()
    (s / "servidor" / "__pycache__" / "app.cpython-312.pyc").write_bytes(b"\0")
    return repo


def test_imagen_es_lista_cerrada(repo_sitio):
    salida = repo_sitio / "build" / "sitio-imagen"
    m = armar_imagen(repo_sitio, salida)
    assert not m["commit"].endswith("-sucio")
    archivos = sorted(str(p.relative_to(salida)) for p in salida.rglob("*") if p.is_file())
    assert archivos == ["Dockerfile", "cloudbuild.yaml", "contenido/a-p.html",
                        "contenido/manifiesto.json", "requirements.txt", "servidor/app.py",
                        "web/estaticos/base.css", "web/login.html"]


def test_imagen_se_niega_con_sitio_sucio(repo_sitio):
    salida = repo_sitio / "build" / "sitio-imagen"
    (repo_sitio / "sitio" / "servidor" / "app.py").write_text("x = 2\n", "utf-8")
    with pytest.raises(ErrorArmado):
        armar_imagen(repo_sitio, salida)
    assert not salida.exists()
    assert armar_imagen(repo_sitio, salida, permitir_sucio=True)["commit"].endswith("-sucio")


def test_imagen_se_niega_con_contenido_sucio(repo_sitio):
    (repo_sitio / "temas" / "a" / "p.html").write_text("<p>cambio</p>", "utf-8")
    with pytest.raises(ErrorArmado):
        armar_imagen(repo_sitio, repo_sitio / "build" / "sitio-imagen")


def test_imagen_no_borra_salidas_peligrosas(repo_sitio):
    for peligrosa in (repo_sitio, repo_sitio.parent, repo_sitio / "sitio" / "algo"):
        with pytest.raises(ErrorArmado):
            armar_imagen(repo_sitio, peligrosa)
    assert (repo_sitio / "sitio" / "servidor" / "app.py").exists()
