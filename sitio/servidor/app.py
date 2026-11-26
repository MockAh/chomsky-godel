"""Aplicación del sitio de estudio (specs 01 y 02).

`crear_app` recibe el almacén y el reloj: así las mismas pruebas corren contra
memoria y contra Firestore, y se puede simular el paso del tiempo.
"""
from __future__ import annotations

import hmac
import json
import re
import time
from pathlib import Path
from typing import Callable, Literal
from urllib.parse import urlsplit

from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, JSONResponse, RedirectResponse, Response
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from . import anotaciones, seguridad

DIR_WEB = Path(__file__).resolve().parent.parent / "web"

COOKIE = "__Host-sesion"
DURACION_SESION = 7 * 24 * 3600
DURACION_INVITACION = 14 * 24 * 3600
MAX_INTENTOS = 5
VENTANA_INTENTOS = 15 * 60
ROLES = ("admin", "tester")
ID_VALIDO = re.compile(r"^[a-z0-9-]+$")
SECCION_IMPLICITA = {"id": "general", "nombre": "General"}

CSP_SITIO = ("default-src 'self'; frame-src 'self'; base-uri 'none'; "
             "form-action 'self'; frame-ancestors 'none'")
# script-src 'self': las lecciones 3D cargan Three.js de /estaticos/vendor (P-7).
CSP_CONTENIDO = ("default-src 'none'; script-src 'self' 'unsafe-inline'; "
                 "style-src 'unsafe-inline' https://fonts.googleapis.com; "
                 "font-src https://fonts.gstatic.com; img-src data: blob:; "
                 "base-uri 'none'; form-action 'none'; frame-ancestors 'self'")
ENCABEZADOS = {
    "Cache-Control": "no-store",
    "X-Robots-Tag": "noindex, nofollow",
    "X-Content-Type-Options": "nosniff",
    "Referrer-Policy": "same-origin",
    "Strict-Transport-Security": "max-age=31536000",
}

MSG_CREDENCIALES = "Usuario o contraseña incorrectos."
MSG_DEMASIADOS = "Demasiados intentos. Espera 15 minutos."
MSG_ENLACE = "Este enlace ya se usó o venció."
MSG_SIN_SESION = "Sin sesión."
MSG_NO_EXISTE = "No existe."
HUELLA_VALIDA = re.compile(r"^[0-9a-f]{64}$")


# ---------- cuerpos de las peticiones ----------

class DatosLogin(BaseModel):
    correo: str = Field(min_length=3, max_length=254)
    contrasena: str = Field(min_length=1, max_length=256)


class DatosActivar(BaseModel):
    ficha: str = Field(min_length=1, max_length=128)
    contrasena: str = Field(min_length=1, max_length=256)


class DatosCambio(BaseModel):
    actual: str = Field(min_length=1, max_length=256)
    nueva: str = Field(min_length=1, max_length=256)


class DatosNota(BaseModel):
    texto: str = Field(max_length=20_000)


class DatosNotaElemento(DatosNota):
    titulo: str = Field(min_length=1, max_length=200)
    tipo: Literal["ejercicio", "circuito", "pregunta", "lectura"]
    estado: str = Field(default="", max_length=40)


# ---------- utilidades ----------

def normalizar_correo(correo: str) -> str:
    return correo.strip().lower()


def emitir_invitacion(almacen, correo: str, rol: str, ahora: float) -> str:
    """Crea una invitación y devuelve la ficha (va en el enlace, nunca en la base).

    Lanza CuentaYaActiva si el correo ya tiene cuenta.
    """
    if rol not in ROLES:
        raise ValueError(f"Rol desconocido: {rol}")
    ficha = seguridad.nueva_ficha()
    almacen.crear_invitacion(seguridad.huella(ficha), normalizar_correo(correo), rol,
                             ahora + DURACION_INVITACION)
    return ficha


def cargar_manifiesto(dir_contenido: Path) -> dict:
    """Lee contenido/manifiesto.json (lo escribe armar_contenido.py) y lo valida."""
    datos = json.loads((dir_contenido / "manifiesto.json").read_text("utf-8"))
    temas = []
    for t in datos["temas"]:
        if not ID_VALIDO.match(t["id"]):
            raise ValueError(f"id de tema inválido: {t['id']!r}")
        for p in t["pestanas"]:
            if not ID_VALIDO.match(p["id"]):
                raise ValueError(f"id de pestaña inválido: {t['id']}/{p['id']!r}")
        temas.append({
            "id": t["id"], "corto": t["corto"], "nombre": t["nombre"], "grupo": t.get("grupo", ""),
            "secciones": t.get("secciones") or [dict(SECCION_IMPLICITA)],
            "pestanas": [{
                "id": p["id"], "etiqueta": p["etiqueta"], "anotable": bool(p["anotable"]),
                "version": p["version"], "sha256": p["sha256"], "aviso": p.get("aviso", ""),
                "en": p.get("en") or {},
            } for p in t["pestanas"]],
            "en": t.get("en") or {},
        })
    return {"commit": datos.get("commit", ""), "temas": temas}


def _error(estado: int, detalle: str, **extra) -> JSONResponse:
    return JSONResponse({"detalle": detalle, **extra}, status_code=estado)


# ---------- la aplicación ----------

def crear_app(almacen, dir_contenido, reloj: Callable[[], float] = time.time,
              huella_museo: str | None = None) -> FastAPI:
    """`huella_museo`: sha256 de la clave del enlace de solo lectura (P-34); sin ella no hay museo."""
    dir_contenido = Path(dir_contenido)
    if huella_museo and not HUELLA_VALIDA.match(huella_museo):
        huella_museo = None  # mal configurada: el museo queda cerrado
    manifiesto = cargar_manifiesto(dir_contenido)
    temas = {t["id"]: t for t in manifiesto["temas"]}

    app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)

    @app.middleware("http")
    async def encabezados_y_origen(request: Request, call_next):
        if request.method not in ("GET", "HEAD"):
            origen = request.headers.get("origin")
            host = request.headers.get("host")
            if not origen or not host or urlsplit(origen).netloc != host:
                respuesta = _error(403, "Origen no permitido.")
            else:
                respuesta = await call_next(request)
        else:
            respuesta = await call_next(request)
        if "content-security-policy" not in respuesta.headers:
            respuesta.headers["Content-Security-Policy"] = CSP_SITIO
        respuesta.headers.update(ENCABEZADOS)
        return respuesta

    # --- sesión ---

    def sesion_actual(request: Request) -> dict | None:
        ficha = request.cookies.get(COOKIE)
        if not ficha or len(ficha) > 128:
            return None
        h = seguridad.huella(ficha)
        s = almacen.obtener_sesion(h)
        if not s:
            return None
        if s["expira"] <= reloj():
            almacen.borrar_sesion(h)
            return None
        usuario = almacen.obtener_usuario(s["correo"])
        if not usuario:
            almacen.borrar_sesion(h)
            return None
        return {"correo": usuario["correo"], "rol": usuario["rol"], "huella": h}

    def abrir_sesion(respuesta: Response, correo: str) -> None:
        ficha = seguridad.nueva_ficha()
        almacen.crear_sesion(seguridad.huella(ficha), correo, reloj() + DURACION_SESION)
        respuesta.set_cookie(COOKIE, ficha, max_age=DURACION_SESION, path="/",
                             secure=True, httponly=True, samesite="lax")

    # --- páginas ---

    def pagina(nombre: str) -> FileResponse:
        return FileResponse(DIR_WEB / nombre, media_type="text/html")

    @app.get("/login")
    def ver_login(request: Request):
        if sesion_actual(request):
            return RedirectResponse("/", status_code=302)
        return pagina("login.html")

    @app.get("/activar")
    def ver_activar():
        return pagina("activar.html")

    @app.get("/")
    def ver_temas(request: Request):
        if not sesion_actual(request):
            return RedirectResponse("/login", status_code=302)
        return pagina("temas.html")

    @app.get("/t/{tema}")
    def ver_tema(tema: str, request: Request):
        if not sesion_actual(request):
            return RedirectResponse("/login", status_code=302)
        if tema not in temas:
            return _error(404, "Ese tema no existe.")
        return pagina("tema.html")

    def servir_contenido(tema: str, pestana: str, idioma: str = "es"):
        t = temas.get(tema)
        p = next((p for p in t["pestanas"] if p["id"] == pestana), None) if t else None
        if not p:
            return _error(404, "Ese contenido no existe.")
        sufijo = ".en" if idioma == "en" and p["en"].get("sha256") else ""
        return FileResponse(dir_contenido / f"{tema}-{pestana}{sufijo}.html", media_type="text/html",
                            headers={"Content-Security-Policy": CSP_CONTENIDO})

    @app.get("/contenido/{tema}/{pestana}")
    def ver_contenido(tema: str, pestana: str, request: Request):
        if not sesion_actual(request):
            return _error(401, MSG_SIN_SESION)
        return servir_contenido(tema, pestana)

    # --- museo: solo lectura con enlace secreto (P-34) ---
    # Solo GET, sin cookies y sin tocar el almacén. Clave equivocada = 404, igual que una ruta
    # que no existe, para no confirmar que el museo existe.

    def es_museo(clave: str) -> bool:
        return bool(huella_museo) and len(clave) <= 128 and hmac.compare_digest(
            seguridad.huella(clave), huella_museo)

    def temas_museo(idioma: str) -> list[dict]:
        """La lista para el museo, sin huellas ni secciones. En inglés (P-35) usa los nombres
        en inglés si los hay y marca `solo_es` las pestañas que aún no tienen traducción."""
        def texto(d: dict, campo: str) -> str:
            return (d["en"].get(campo) or d[campo]) if idioma == "en" else d[campo]
        return [{
            "id": t["id"], "corto": texto(t, "corto"), "nombre": texto(t, "nombre"), "grupo": t["grupo"],
            "pestanas": [{"id": p["id"], "etiqueta": texto(p, "etiqueta"), "version": p["version"],
                          "aviso": texto(p, "aviso") if p["aviso"] else "", "anotable": False,
                          "solo_es": idioma == "en" and not p["en"].get("sha256")}
                         for p in t["pestanas"]],
        } for t in manifiesto["temas"]]

    listas_museo = {"es": temas_museo("es"), "en": temas_museo("en")}

    def rutas_museo(prefijo: str, idioma: str) -> None:
        @app.get(f"/m/{{clave}}{prefijo}", name=f"museo_entrada_{idioma}")
        def entrada(clave: str):
            return pagina("login.html") if es_museo(clave) else _error(404, MSG_NO_EXISTE)

        @app.get(f"/m/{{clave}}{prefijo}/temas", name=f"museo_temas_{idioma}")
        def lista(clave: str):
            return pagina("temas.html") if es_museo(clave) else _error(404, MSG_NO_EXISTE)

        @app.get(f"/m/{{clave}}{prefijo}/t/{{tema}}", name=f"museo_tema_{idioma}")
        def tema(clave: str, tema: str):
            if not es_museo(clave) or tema not in temas:
                return _error(404, MSG_NO_EXISTE)
            return pagina("tema.html")

        @app.get(f"/m/{{clave}}{prefijo}/contenido/{{tema}}/{{pestana}}", name=f"museo_contenido_{idioma}")
        def contenido(clave: str, tema: str, pestana: str):
            if not es_museo(clave):
                return _error(404, MSG_NO_EXISTE)
            return servir_contenido(tema, pestana, idioma)

        @app.get(f"/m/{{clave}}{prefijo}/api/temas", name=f"museo_api_temas_{idioma}")
        def api_temas(clave: str):
            return {"temas": listas_museo[idioma]} if es_museo(clave) else _error(404, MSG_NO_EXISTE)

    # Español en /m/<clave>/…, inglés en /m/<clave>/en/… (P-35)
    rutas_museo("", "es")
    rutas_museo("/en", "en")

    @app.get("/salud", status_code=204)
    def salud():
        return Response(status_code=204)

    # --- API de cuentas ---

    @app.post("/api/login")
    def login(datos: DatosLogin):
        correo = normalizar_correo(datos.correo)
        clave = seguridad.huella(correo)
        if not almacen.reservar_intento(clave, MAX_INTENTOS, VENTANA_INTENTOS, reloj()):
            return _error(429, MSG_DEMASIADOS)
        usuario = almacen.obtener_usuario(correo)
        hash_ = usuario["hash"] if usuario else seguridad.HASH_FALSO
        if not seguridad.verificar(hash_, datos.contrasena) or not usuario:
            return _error(401, MSG_CREDENCIALES)
        almacen.limpiar_intentos(clave)
        respuesta = JSONResponse({"ok": True})
        abrir_sesion(respuesta, correo)
        return respuesta

    @app.post("/api/activar")
    def activar(datos: DatosActivar):
        h = seguridad.huella(datos.ficha)
        ahora = reloj()
        if not almacen.obtener_invitacion(h, ahora):
            return _error(410, MSG_ENLACE)
        errores = seguridad.errores_contrasena(datos.contrasena)
        if errores:  # el enlace sigue sirviendo
            return _error(422, "La contraseña no cumple la regla.", errores=errores)
        usuario = almacen.activar_invitacion(h, seguridad.hashear(datos.contrasena), ahora)
        if not usuario:
            return _error(410, MSG_ENLACE)
        respuesta = JSONResponse({"ok": True})
        abrir_sesion(respuesta, usuario["correo"])
        return respuesta

    @app.post("/api/contrasena")
    def cambiar_contrasena(datos: DatosCambio, request: Request):
        sesion = sesion_actual(request)
        if not sesion:
            return _error(401, MSG_SIN_SESION)
        correo = sesion["correo"]
        clave = seguridad.huella("cambio|" + correo)
        if not almacen.reservar_intento(clave, MAX_INTENTOS, VENTANA_INTENTOS, reloj()):
            return _error(429, MSG_DEMASIADOS)
        usuario = almacen.obtener_usuario(correo)
        if not seguridad.verificar(usuario["hash"], datos.actual):
            return _error(403, "La contraseña actual no es correcta.")
        errores = seguridad.errores_contrasena(datos.nueva)
        if errores:
            return _error(422, "La contraseña no cumple la regla.", errores=errores)
        almacen.cambiar_contrasena(correo, seguridad.hashear(datos.nueva))
        almacen.limpiar_intentos(clave)
        almacen.borrar_sesiones_de(correo)
        respuesta = JSONResponse({"ok": True})
        abrir_sesion(respuesta, correo)
        return respuesta

    @app.post("/api/logout")
    def logout(request: Request):
        ficha = request.cookies.get(COOKIE)
        if ficha and len(ficha) <= 128:
            almacen.borrar_sesion(seguridad.huella(ficha))
        respuesta = JSONResponse({"ok": True})
        respuesta.delete_cookie(COOKIE, path="/", secure=True, httponly=True, samesite="lax")
        return respuesta

    @app.get("/api/sesion")
    def ver_sesion(request: Request):
        sesion = sesion_actual(request)
        if not sesion:
            return _error(401, MSG_SIN_SESION)
        return {"correo": sesion["correo"], "rol": sesion["rol"],
                "temas": manifiesto["temas"]}

    # --- anotaciones ---

    hashes_vigentes = anotaciones.vigentes(manifiesto["temas"])

    def pestana_anotable(tema: str, pestana: str, seccion: str) -> dict | None:
        t = temas.get(tema)
        if not t or seccion not in {s["id"] for s in t["secciones"]}:
            return None
        p = next((p for p in t["pestanas"] if p["id"] == pestana), None)
        return p if p and p["anotable"] else None

    @app.get("/api/anotaciones/exportar")
    def exportar(request: Request):
        sesion = sesion_actual(request)
        if not sesion:
            return _error(401, MSG_SIN_SESION)
        if sesion["rol"] != "admin":
            return _error(403, "Solo el admin puede exportar.")
        ahora = reloj()
        texto = anotaciones.a_markdown(almacen.listar_anotaciones(), manifiesto, ahora)
        nombre = time.strftime("anotaciones-chomsky-godel-%Y%m%d.md", time.gmtime(ahora))
        return Response(texto, media_type="text/markdown; charset=utf-8",
                        headers={"Content-Disposition": f'attachment; filename="{nombre}"'})

    @app.get("/api/anotaciones/{tema}")
    def ver_anotaciones(tema: str, request: Request):
        sesion = sesion_actual(request)
        if not sesion:
            return _error(401, MSG_SIN_SESION)
        if tema not in temas:
            return _error(404, "Ese tema no existe.")
        return anotaciones.visibles(almacen.listar_anotaciones(tema), sesion["correo"],
                                    sesion["rol"] == "admin", hashes_vigentes)

    def guardar_nota(request: Request, tema: str, pestana: str, seccion: str,
                     texto: str, elemento: dict | None):
        sesion = sesion_actual(request)
        if not sesion:
            return _error(401, MSG_SIN_SESION)
        p = pestana_anotable(tema, pestana, seccion)
        if not p:
            return _error(404, "Esa sección no admite anotaciones.")
        ahora = reloj()
        almacen.guardar_anotacion(tema, pestana, seccion, sesion["correo"], sesion["rol"],
                                  p["sha256"], p["version"], texto, ahora, elemento=elemento)
        return {"ok": True, "actualizada": ahora}

    @app.put("/api/anotaciones/{tema}/{pestana}/{seccion}")
    def guardar_seccion(tema: str, pestana: str, seccion: str, datos: DatosNota, request: Request):
        return guardar_nota(request, tema, pestana, seccion, datos.texto, None)

    @app.put("/api/anotaciones/{tema}/{pestana}/{seccion}/elemento")
    def guardar_elemento(tema: str, pestana: str, seccion: str, datos: DatosNotaElemento,
                         request: Request):
        elemento = {"clave": anotaciones.clave_elemento(seccion, datos.titulo),
                    "titulo": datos.titulo, "tipo": datos.tipo, "estado": datos.estado}
        return guardar_nota(request, tema, pestana, seccion, datos.texto, elemento)

    app.mount("/estaticos", StaticFiles(directory=DIR_WEB / "estaticos"), name="estaticos")
    return app
