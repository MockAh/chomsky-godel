"""Almacén en memoria (pruebas y uso local). Contrato en spec 02 §3.

AlmacenFirestore implementa exactamente los mismos métodos.
"""
from __future__ import annotations

import copy
import threading

from .seguridad import huella


class CuentaYaActiva(Exception):
    """Se intentó invitar a un correo que ya tiene cuenta."""


def id_anotacion(tema, pestana, seccion, elemento, autor, version_hash) -> str:
    clave = elemento["clave"] if elemento else ""
    return huella("|".join([tema, pestana, seccion, clave, autor, version_hash]))


class AlmacenMemoria:
    def __init__(self):
        self._lock = threading.RLock()  # hace las veces de transacción
        self.usuarios: dict[str, dict] = {}
        self.invitaciones: dict[str, dict] = {}
        self.sesiones: dict[str, dict] = {}
        self.intentos: dict[str, dict] = {}
        self.anotaciones: dict[str, dict] = {}

    # --- usuarios ---
    def guardar_usuario(self, correo, hash_, rol):
        with self._lock:
            self.usuarios[correo] = {"correo": correo, "hash": hash_, "rol": rol}

    def obtener_usuario(self, correo):
        with self._lock:
            u = self.usuarios.get(correo)
            return dict(u) if u else None

    def cambiar_contrasena(self, correo, hash_):
        with self._lock:
            if correo in self.usuarios:
                self.usuarios[correo]["hash"] = hash_

    # --- invitaciones ---
    def crear_invitacion(self, huella_, correo, rol, expira):
        with self._lock:
            if correo in self.usuarios:
                raise CuentaYaActiva(correo)
            for h in [h for h, i in self.invitaciones.items() if i["correo"] == correo]:
                del self.invitaciones[h]
            self.invitaciones[huella_] = {"correo": correo, "rol": rol, "expira": expira}

    def obtener_invitacion(self, huella_, ahora):
        with self._lock:
            inv = self.invitaciones.get(huella_)
            if not inv or inv["expira"] <= ahora:
                return None
            return dict(inv)

    def activar_invitacion(self, huella_, hash_, ahora):
        """Crea la cuenta y borra la invitación en una sola operación atómica."""
        with self._lock:
            inv = self.obtener_invitacion(huella_, ahora)
            if not inv:
                return None
            del self.invitaciones[huella_]
            if inv["correo"] in self.usuarios:
                return None
            self.guardar_usuario(inv["correo"], hash_, inv["rol"])
            return self.obtener_usuario(inv["correo"])

    # --- sesiones ---
    def crear_sesion(self, huella_, correo, expira):
        with self._lock:
            self.sesiones[huella_] = {"correo": correo, "expira": expira}

    def obtener_sesion(self, huella_):
        with self._lock:
            s = self.sesiones.get(huella_)
            return dict(s) if s else None

    def borrar_sesion(self, huella_):
        with self._lock:
            self.sesiones.pop(huella_, None)

    def borrar_sesiones_de(self, correo):
        with self._lock:
            for h in [h for h, s in self.sesiones.items() if s["correo"] == correo]:
                del self.sesiones[h]

    # --- límite de intentos ---
    def reservar_intento(self, clave, maximo, ventana, ahora):
        """Cuenta el intento antes de verificar. False si ya se agotaron."""
        with self._lock:
            reg = self.intentos.get(clave)
            if not reg or ahora - reg["inicio"] >= ventana:
                self.intentos[clave] = {"n": 1, "inicio": ahora}
                return True
            if reg["n"] >= maximo:
                return False
            reg["n"] += 1
            return True

    def limpiar_intentos(self, clave):
        with self._lock:
            self.intentos.pop(clave, None)

    # --- anotaciones ---
    def guardar_anotacion(self, tema, pestana, seccion, autor, rol, version_hash, version,
                          texto, ahora, elemento=None):
        with self._lock:
            id_ = id_anotacion(tema, pestana, seccion, elemento, autor, version_hash)
            previa = self.anotaciones.get(id_)
            self.anotaciones[id_] = {
                "tema": tema, "pestana": pestana, "seccion": seccion,
                "elemento": copy.deepcopy(elemento), "autor": autor, "rol": rol,
                "version_hash": version_hash, "version": version, "texto": texto,
                "creada": previa["creada"] if previa else ahora, "actualizada": ahora,
            }

    def listar_anotaciones(self, tema=None):
        with self._lock:
            return [copy.deepcopy(a) for a in self.anotaciones.values()
                    if tema is None or a["tema"] == tema]
