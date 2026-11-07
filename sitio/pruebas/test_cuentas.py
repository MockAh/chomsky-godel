"""Cuentas, sesiones, invitaciones y protección CSRF (spec 05 §1)."""
import pytest

from conftest import ADMIN, CONTRASENA, TESTER, entrar, nuevo_cliente
from servidor import seguridad
from servidor.almacen import CuentaYaActiva
from servidor.app import MSG_CREDENCIALES, MSG_DEMASIADOS, MSG_ENLACE, emitir_invitacion

NUEVA = "Otra-Clave-Segura-2"


def test_sin_sesion_redirige_o_niega(cliente):
    for ruta in ("/", "/t/logica", "/t/x"):
        r = cliente.get(ruta)
        assert r.status_code == 302 and r.headers["location"] == "/login"
    assert cliente.get("/contenido/logica/practica").status_code == 401
    assert cliente.get("/api/sesion").status_code == 401


def test_login_correcto_da_cookie_segura(cliente):
    r = entrar(cliente)
    assert r.status_code == 200
    cookie = r.headers["set-cookie"].lower()
    assert cookie.startswith("__host-sesion=")
    for atributo in ("secure", "httponly", "samesite=lax", "path=/", "max-age=604800"):
        assert atributo in cookie
    s = cliente.get("/api/sesion").json()
    assert s["correo"] == TESTER and s["rol"] == "tester"
    assert cliente.get("/login").headers["location"] == "/"


def test_correo_inexistente_y_contrasena_mala_dan_lo_mismo(cliente):
    a = entrar(cliente, correo="nadie@ejemplo.org")
    b = entrar(cliente, contrasena="Incorrecta-123!")
    assert a.status_code == b.status_code == 401
    assert a.json() == b.json() == {"detalle": MSG_CREDENCIALES}


def test_limite_de_intentos(cliente, reloj):
    for _ in range(5):
        assert entrar(cliente, contrasena="Mala-Mala-123!").status_code == 401
    r = entrar(cliente)  # el 6.º, aunque sea correcto
    assert r.status_code == 429 and r.json()["detalle"] == MSG_DEMASIADOS
    reloj.avanzar(15 * 60)
    assert entrar(cliente).status_code == 200


def test_entrar_bien_reinicia_el_contador(cliente):
    for _ in range(4):
        entrar(cliente, contrasena="Mala-Mala-123!")
    assert entrar(cliente).status_code == 200
    for _ in range(5):
        assert entrar(cliente, contrasena="Mala-Mala-123!").status_code == 401


def test_sesion_vencida(cliente, reloj, almacen):
    entrar(cliente)
    reloj.avanzar(7 * 24 * 3600)
    assert cliente.get("/api/sesion").status_code == 401
    assert almacen.sesiones == {}


def test_invitacion_un_solo_uso(app, almacen, reloj):
    ficha = emitir_invitacion(almacen, "Nueva@Ejemplo.org", "tester", reloj())
    assert ficha not in str(almacen.invitaciones)  # solo se guarda la huella
    c = nuevo_cliente(app)
    r = c.post("/api/activar", json={"ficha": ficha, "contrasena": NUEVA})
    assert r.status_code == 200
    assert c.get("/api/sesion").json()["correo"] == "nueva@ejemplo.org"
    r = c.post("/api/activar", json={"ficha": ficha, "contrasena": NUEVA})
    assert r.status_code == 410 and r.json()["detalle"] == MSG_ENLACE


def test_invitacion_vencida(cliente, almacen, reloj):
    ficha = emitir_invitacion(almacen, "nueva@ejemplo.org", "tester", reloj())
    reloj.avanzar(14 * 24 * 3600)
    assert cliente.post("/api/activar", json={"ficha": ficha, "contrasena": NUEVA}).status_code == 410


def test_contrasena_debil_no_gasta_el_enlace(cliente, almacen, reloj):
    ficha = emitir_invitacion(almacen, "nueva@ejemplo.org", "tester", reloj())
    r = cliente.post("/api/activar", json={"ficha": ficha, "contrasena": "corta"})
    assert r.status_code == 422 and r.json()["errores"]
    assert cliente.post("/api/activar", json={"ficha": ficha, "contrasena": NUEVA}).status_code == 200


def test_cuenta_activa_no_recibe_invitacion(almacen, reloj):
    with pytest.raises(CuentaYaActiva):
        emitir_invitacion(almacen, TESTER, "tester", reloj())


def test_nueva_invitacion_anula_la_anterior(cliente, almacen, reloj):
    vieja = emitir_invitacion(almacen, "nueva@ejemplo.org", "tester", reloj())
    nueva = emitir_invitacion(almacen, "nueva@ejemplo.org", "tester", reloj())
    assert cliente.post("/api/activar", json={"ficha": vieja, "contrasena": NUEVA}).status_code == 410
    assert cliente.post("/api/activar", json={"ficha": nueva, "contrasena": NUEVA}).status_code == 200


def test_cambiar_contrasena_cierra_las_demas_sesiones(app):
    uno, otro = nuevo_cliente(app), nuevo_cliente(app)
    entrar(uno)
    entrar(otro)
    r = uno.post("/api/contrasena", json={"actual": CONTRASENA, "nueva": NUEVA})
    assert r.status_code == 200
    assert uno.get("/api/sesion").status_code == 200
    assert otro.get("/api/sesion").status_code == 401
    assert entrar(nuevo_cliente(app), contrasena=NUEVA).status_code == 200
    assert entrar(nuevo_cliente(app)).status_code == 401


def test_cambiar_contrasena_valida_actual_y_regla(cliente):
    entrar(cliente)
    assert cliente.post("/api/contrasena", json={"actual": "Mal-Mal-1234!", "nueva": NUEVA}).status_code == 403
    assert cliente.post("/api/contrasena", json={"actual": CONTRASENA, "nueva": "debil"}).status_code == 422


def test_post_sin_origin_o_con_otro_origin(app):
    for origen in (None, "https://otro.sitio", "null"):
        r = nuevo_cliente(app, origen).post("/api/login", json={"correo": ADMIN, "contrasena": CONTRASENA})
        assert r.status_code == 403


def test_salir(cliente, almacen):
    entrar(cliente)
    assert cliente.post("/api/logout").status_code == 200
    assert cliente.get("/api/sesion").status_code == 401
    assert almacen.sesiones == {}


def test_politica_de_contrasenas():
    assert seguridad.errores_contrasena("Correcta-Larga-1") == []
    assert len(seguridad.errores_contrasena("abc")) == 4  # corta, sin mayúscula, número ni símbolo
