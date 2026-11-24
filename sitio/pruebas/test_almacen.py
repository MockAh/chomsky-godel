"""Pruebas de contrato del almacén (spec 02 §3 y 05 §1).

Las mismas pruebas corren contra AlmacenMemoria y contra AlmacenFirestore en el
emulador de Firestore (fixture `emulador` de conftest.py), con un prefijo de
colecciones por prueba.
"""
import uuid

import pytest

from servidor.almacen import AlmacenMemoria, CuentaYaActiva


@pytest.fixture(params=["memoria", "firestore"])
def alm(request):
    if request.param == "memoria":
        return AlmacenMemoria()
    cliente = request.getfixturevalue("emulador")
    from servidor.almacen_firestore import AlmacenFirestore
    return AlmacenFirestore(cliente, prefijo=f"prueba-{uuid.uuid4().hex[:8]}-")


def test_usuarios(alm):
    assert alm.obtener_usuario("a@x.org") is None
    alm.guardar_usuario("a@x.org", "h1", "admin")
    alm.cambiar_contrasena("a@x.org", "h2")
    assert alm.obtener_usuario("a@x.org") == {"correo": "a@x.org", "hash": "h2", "rol": "admin"}


def test_invitaciones(alm):
    alm.crear_invitacion("i1", "b@x.org", "tester", expira=100)
    assert alm.obtener_invitacion("i1", ahora=50)["correo"] == "b@x.org"
    assert alm.obtener_invitacion("i1", ahora=100) is None
    alm.crear_invitacion("i2", "b@x.org", "tester", expira=200)
    assert alm.obtener_invitacion("i1", ahora=50) is None  # la nueva anula la anterior
    assert alm.activar_invitacion("i2", "h", ahora=50)["rol"] == "tester"
    assert alm.obtener_invitacion("i2", ahora=50) is None
    assert alm.activar_invitacion("i2", "h", ahora=50) is None
    with pytest.raises(CuentaYaActiva):
        alm.crear_invitacion("i3", "b@x.org", "tester", expira=200)


def test_sesiones(alm):
    alm.crear_sesion("s1", "a@x.org", 10)
    alm.crear_sesion("s2", "a@x.org", 10)
    alm.crear_sesion("s3", "b@x.org", 10)
    alm.borrar_sesion("s1")
    assert alm.obtener_sesion("s1") is None
    alm.borrar_sesiones_de("a@x.org")
    assert alm.obtener_sesion("s2") is None and alm.obtener_sesion("s3")["correo"] == "b@x.org"


def test_intentos(alm):
    assert all(alm.reservar_intento("k", 5, 900, ahora=0) for _ in range(5))
    assert not alm.reservar_intento("k", 5, 900, ahora=899)
    assert alm.reservar_intento("k", 5, 900, ahora=900)
    alm.limpiar_intentos("k")
    assert all(alm.reservar_intento("k", 5, 900, ahora=901) for _ in range(5))


def test_anotaciones(alm):
    args = dict(tema="t", pestana="p", seccion="s1", autor="a@x.org", rol="admin",
                version_hash="h1", version="v0.1")
    alm.guardar_anotacion(**args, texto="uno", ahora=1)
    alm.guardar_anotacion(**args, texto="dos", ahora=2)
    alm.guardar_anotacion(**{**args, "version_hash": "h2"}, texto="tres", ahora=3)
    elem = {"clave": "abc", "titulo": "Ej 4", "tipo": "ejercicio", "estado": "resuelto"}
    alm.guardar_anotacion(**args, texto="cuatro", ahora=4, elemento=elem)
    alm.guardar_anotacion(**{**args, "tema": "otro"}, texto="cinco", ahora=5)
    notas = alm.listar_anotaciones("t")
    assert len(notas) == 3 and len(alm.listar_anotaciones()) == 4
    misma = next(n for n in notas if n["version_hash"] == "h1" and n["elemento"] is None)
    assert (misma["texto"], misma["creada"], misma["actualizada"]) == ("dos", 1, 2)


def test_invitacion_repetida_con_la_misma_huella(alm):
    alm.crear_invitacion("i1", "c@x.org", "tester", expira=100)
    alm.crear_invitacion("i1", "c@x.org", "admin", expira=200)
    assert alm.obtener_invitacion("i1", ahora=150)["rol"] == "admin"


def test_activar_vencida_o_inexistente(alm):
    alm.crear_invitacion("i1", "d@x.org", "tester", expira=100)
    assert alm.activar_invitacion("i1", "h", ahora=100) is None
    assert alm.activar_invitacion("nada", "h", ahora=1) is None
    assert alm.obtener_usuario("d@x.org") is None
