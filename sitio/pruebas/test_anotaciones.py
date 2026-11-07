"""Anotaciones: guardar, leer, versiones, visibilidad por rol y exportación (spec 05 §1)."""
import json

from conftest import ADMIN, TESTER, entrar, nuevo_cliente
from servidor.app import crear_app

URL = "/api/anotaciones/logica/practica"


def nota(c, seccion, texto):
    return c.put(f"{URL}/{seccion}", json={"texto": texto})


def nota_elemento(c, seccion, titulo, texto, tipo="ejercicio", estado="resuelto"):
    return c.put(f"{URL}/{seccion}/elemento",
                 json={"texto": texto, "titulo": titulo, "tipo": tipo, "estado": estado})


def test_guardar_y_leer(cliente, reloj):
    entrar(cliente)
    assert nota(cliente, "s1", "primera").status_code == 200
    reloj.avanzar(10)
    assert nota(cliente, "s1", "corregida").status_code == 200
    assert nota_elemento(cliente, "s2", "Ejercicio 4: XOR con NAND", "duda").status_code == 200
    g = cliente.get("/api/anotaciones/logica").json()
    assert "de_otros" not in g  # el tester no recibe ese grupo
    (m,) = g["mias"]
    assert (m["seccion"], m["texto"], m["version"], m["autor_rol"]) == ("s1", "corregida", "v0.1", "Tester")
    assert m["actualizada"] - m["creada"] == 10
    (e,) = g["mias_elementos"]
    assert e["elemento"]["titulo"] == "Ejercicio 4: XOR con NAND" and len(e["elemento"]["clave"]) == 16
    assert g["anteriores"] == []


def test_cambiar_el_archivo_pasa_las_notas_a_anteriores(almacen, contenido, reloj):
    c = nuevo_cliente(crear_app(almacen, contenido, reloj=reloj))
    entrar(c)
    nota(c, "s1", "sobre v0.1")
    nota(c, "s2", "")  # vacía: no aparece en «anteriores»
    m = json.loads((contenido / "manifiesto.json").read_text("utf-8"))
    m["temas"][0]["pestanas"][0].update(sha256="otro-archivo", version="v0.2")
    (contenido / "manifiesto.json").write_text(json.dumps(m), "utf-8")
    c2 = nuevo_cliente(crear_app(almacen, contenido, reloj=reloj))
    entrar(c2)
    g = c2.get("/api/anotaciones/logica").json()
    assert g["mias"] == []
    assert [(n["texto"], n["version"]) for n in g["anteriores"]] == [("sobre v0.1", "v0.1")]
    nota(c2, "s1", "sobre v0.2")
    g = c2.get("/api/anotaciones/logica").json()
    assert g["mias"][0]["version"] == "v0.2" and len(g["anteriores"]) == 1


def test_cambiar_solo_la_etiqueta_no_reinicia(almacen, contenido, reloj):
    c = nuevo_cliente(crear_app(almacen, contenido, reloj=reloj))
    entrar(c)
    nota(c, "s1", "texto")
    m = json.loads((contenido / "manifiesto.json").read_text("utf-8"))
    m["temas"][0]["pestanas"][0]["version"] = "v0.1.1"
    (contenido / "manifiesto.json").write_text(json.dumps(m), "utf-8")
    c2 = nuevo_cliente(crear_app(almacen, contenido, reloj=reloj))
    entrar(c2)
    assert c2.get("/api/anotaciones/logica").json()["mias"][0]["texto"] == "texto"


def test_visibilidad_por_rol(app):
    tester, admin = nuevo_cliente(app), nuevo_cliente(app)
    entrar(tester)
    entrar(admin, correo=ADMIN)
    nota(tester, "s1", "nota del tester")
    nota(admin, "s1", "nota del admin")
    gt = tester.get("/api/anotaciones/logica").json()
    assert [n["texto"] for n in gt["mias"]] == ["nota del tester"]
    assert "nota del admin" not in json.dumps(gt)
    ga = admin.get("/api/anotaciones/logica").json()
    assert [n["texto"] for n in ga["mias"]] == ["nota del admin"]
    assert [(n["texto"], n["autor_rol"]) for n in ga["de_otros"]] == [("nota del tester", "Tester")]
    for cuerpo in (json.dumps(gt), json.dumps(ga)):
        assert TESTER not in cuerpo and ADMIN not in cuerpo and '"autor"' not in cuerpo


def test_exportar(app):
    tester, admin = nuevo_cliente(app), nuevo_cliente(app)
    entrar(tester)
    entrar(admin, correo=ADMIN)
    nota(tester, "s2", "compuertas: NAND basta")
    nota_elemento(admin, "s1", "Ejercicio 1", "De Morgan")
    assert tester.get("/api/anotaciones/exportar").status_code == 403
    r = admin.get("/api/anotaciones/exportar")
    assert r.status_code == 200 and r.headers["content-type"].startswith("text/markdown")
    assert "attachment" in r.headers["content-disposition"]
    md = r.text
    assert "## Lógica booleana" in md and "### Práctica · Compuertas" in md
    assert "**Tester**" in md and "**Admin**" in md and "#### Ejercicio 1 (ejercicio, resuelto)" in md
    assert md.index("Ejercicio 1") < md.index("NAND basta")  # s1 antes que s2
    assert TESTER not in md and ADMIN not in md


def test_validaciones(cliente):
    assert nota(cliente, "s1", "x").status_code == 401
    entrar(cliente)
    assert nota(cliente, "s9", "x").status_code == 404           # sección fuera del manifiesto
    assert cliente.put("/api/anotaciones/logica/mapa/s1", json={"texto": "x"}).status_code == 404  # no anotable
    assert cliente.put("/api/anotaciones/nada/practica/s1", json={"texto": "x"}).status_code == 404
    assert cliente.get("/api/anotaciones/nada").status_code == 404
    assert nota(cliente, "s1", "x" * 20_001).status_code == 422
    assert nota_elemento(cliente, "s1", "t", "x", tipo="otro").status_code == 422
    # tema sin secciones: sección implícita «general»
    assert cliente.put("/api/anotaciones/alu/practica/general", json={"texto": "x"}).status_code == 200


def test_put_sin_origin(app):
    c = nuevo_cliente(app)
    entrar(c)
    sin = nuevo_cliente(app, origen=None)
    sin.cookies = c.cookies
    assert sin.put(f"{URL}/s1", json={"texto": "x"}).status_code == 403
