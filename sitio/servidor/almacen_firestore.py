"""Almacén en Firestore (modo nativo). Contrato en spec 02 §3; colecciones en §4.

Mismos métodos y mismas pruebas que AlmacenMemoria. Las operaciones que deben ser
atómicas (activar una invitación, reservar un intento, reemplazar invitaciones)
corren en transacciones de Firestore.

`expira` (segundos) es lo que revisa el código; `borrar_en` (fecha) solo sirve para
que la política TTL de Firestore limpie lo vencido, que puede tardar hasta un día.
"""
from __future__ import annotations

from datetime import datetime, timezone

from google.cloud import firestore
from google.cloud.firestore_v1.base_query import FieldFilter

from .almacen import CuentaYaActiva, id_anotacion


def _fecha(segundos: float) -> datetime:
    return datetime.fromtimestamp(segundos, tz=timezone.utc)


class AlmacenFirestore:
    """`prefijo` antepone un nombre a cada colección (las pruebas usan uno por corrida)."""

    def __init__(self, cliente: firestore.Client | None = None, prefijo: str = ""):
        self.db = cliente or firestore.Client()
        self._usuarios = self.db.collection(prefijo + "usuarios")
        self._invitaciones = self.db.collection(prefijo + "invitaciones")
        self._sesiones = self.db.collection(prefijo + "sesiones")
        self._intentos = self.db.collection(prefijo + "intentos")
        self._anotaciones = self.db.collection(prefijo + "anotaciones")

    # --- usuarios ---
    def guardar_usuario(self, correo, hash_, rol):
        self._usuarios.document(correo).set({"correo": correo, "hash": hash_, "rol": rol})

    def obtener_usuario(self, correo):
        doc = self._usuarios.document(correo).get()
        if not doc.exists:
            return None
        d = doc.to_dict()
        return {"correo": d["correo"], "hash": d["hash"], "rol": d["rol"]}

    def cambiar_contrasena(self, correo, hash_):
        ref = self._usuarios.document(correo)

        @firestore.transactional
        def tx(t):
            if ref.get(transaction=t).exists:
                t.update(ref, {"hash": hash_})

        tx(self.db.transaction())

    # --- invitaciones ---
    def crear_invitacion(self, huella_, correo, rol, expira):
        usuario = self._usuarios.document(correo)
        nueva = self._invitaciones.document(huella_)
        mismas = self._invitaciones.where(filter=FieldFilter("correo", "==", correo))

        @firestore.transactional
        def tx(t):
            if usuario.get(transaction=t).exists:
                raise CuentaYaActiva(correo)
            previas = list(t.get(mismas))
            for d in previas:
                if d.id != huella_:  # una transacción no escribe dos veces el mismo documento
                    t.delete(d.reference)
            t.set(nueva, {"correo": correo, "rol": rol, "expira": expira,
                          "borrar_en": _fecha(expira)})

        tx(self.db.transaction())

    @staticmethod
    def _invitacion_valida(doc, ahora):
        if not doc.exists:
            return None
        d = doc.to_dict()
        if d["expira"] <= ahora:
            return None
        return {"correo": d["correo"], "rol": d["rol"], "expira": d["expira"]}

    def obtener_invitacion(self, huella_, ahora):
        return self._invitacion_valida(self._invitaciones.document(huella_).get(), ahora)

    def activar_invitacion(self, huella_, hash_, ahora):
        """Crea la cuenta y borra la invitación en una sola transacción."""
        ref = self._invitaciones.document(huella_)

        @firestore.transactional
        def tx(t):
            inv = self._invitacion_valida(ref.get(transaction=t), ahora)
            if not inv:
                return None
            usuario = self._usuarios.document(inv["correo"])
            ya_existe = usuario.get(transaction=t).exists
            t.delete(ref)
            if ya_existe:
                return None
            t.set(usuario, {"correo": inv["correo"], "hash": hash_, "rol": inv["rol"]})
            return {"correo": inv["correo"], "hash": hash_, "rol": inv["rol"]}

        return tx(self.db.transaction())

    # --- sesiones ---
    def crear_sesion(self, huella_, correo, expira):
        self._sesiones.document(huella_).set(
            {"correo": correo, "expira": expira, "borrar_en": _fecha(expira)})

    def obtener_sesion(self, huella_):
        doc = self._sesiones.document(huella_).get()
        if not doc.exists:
            return None
        d = doc.to_dict()
        return {"correo": d["correo"], "expira": d["expira"]}

    def borrar_sesion(self, huella_):
        self._sesiones.document(huella_).delete()

    def borrar_sesiones_de(self, correo):
        docs = list(self._sesiones.where(filter=FieldFilter("correo", "==", correo)).stream())
        for i in range(0, len(docs), 400):  # un lote admite hasta 500 escrituras
            lote = self.db.batch()
            for d in docs[i:i + 400]:
                lote.delete(d.reference)
            lote.commit()

    # --- límite de intentos ---
    def reservar_intento(self, clave, maximo, ventana, ahora):
        """Cuenta el intento antes de verificar (en una transacción). False si ya se agotaron."""
        ref = self._intentos.document(clave)

        @firestore.transactional
        def tx(t):
            doc = ref.get(transaction=t)
            reg = doc.to_dict() if doc.exists else None
            if not reg or ahora - reg["inicio"] >= ventana:
                t.set(ref, {"n": 1, "inicio": ahora, "borrar_en": _fecha(ahora + ventana)})
                return True
            if reg["n"] >= maximo:
                return False
            t.update(ref, {"n": reg["n"] + 1})
            return True

        return tx(self.db.transaction())

    def limpiar_intentos(self, clave):
        self._intentos.document(clave).delete()

    # --- anotaciones ---
    def guardar_anotacion(self, tema, pestana, seccion, autor, rol, version_hash, version,
                          texto, ahora, elemento=None):
        ref = self._anotaciones.document(
            id_anotacion(tema, pestana, seccion, elemento, autor, version_hash))

        @firestore.transactional
        def tx(t):
            previa = ref.get(transaction=t)
            creada = previa.to_dict()["creada"] if previa.exists else ahora
            t.set(ref, {
                "tema": tema, "pestana": pestana, "seccion": seccion,
                "elemento": dict(elemento) if elemento else None, "autor": autor, "rol": rol,
                "version_hash": version_hash, "version": version, "texto": texto,
                "creada": creada, "actualizada": ahora,
            })

        tx(self.db.transaction())

    def listar_anotaciones(self, tema=None):
        consulta = (self._anotaciones.where(filter=FieldFilter("tema", "==", tema))
                    if tema is not None else self._anotaciones)
        return [d.to_dict() for d in consulta.stream()]
