"""armar_contenido (spec 05 §1). armar_imagen llega en F6."""
import json
import subprocess

import pytest

from armar_contenido import ErrorArmado, armar


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
