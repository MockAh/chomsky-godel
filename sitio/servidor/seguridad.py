"""Política de contraseñas, hash Argon2id, fichas y huellas (spec 02 §5)."""
from __future__ import annotations

import hashlib
import secrets

from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerificationError

LONGITUD_MINIMA = 12
_hasher = PasswordHasher()  # Argon2id con los parámetros por defecto de argon2-cffi


def errores_contrasena(contrasena: str) -> list[str]:
    """Lista de reglas que no se cumplen; vacía si la contraseña es válida."""
    errores = []
    if len(contrasena) < LONGITUD_MINIMA:
        errores.append(f"Debe tener {LONGITUD_MINIMA} caracteres o más.")
    if not any(c.isupper() for c in contrasena):
        errores.append("Debe tener una mayúscula.")
    if not any(c.islower() for c in contrasena):
        errores.append("Debe tener una minúscula.")
    if not any(c.isdigit() for c in contrasena):
        errores.append("Debe tener un número.")
    if not any(not c.isalnum() and not c.isspace() for c in contrasena):
        errores.append("Debe tener un símbolo.")
    return errores


def hashear(contrasena: str) -> str:
    return _hasher.hash(contrasena)


def verificar(hash_guardado: str, contrasena: str) -> bool:
    try:
        return _hasher.verify(hash_guardado, contrasena)
    except (VerificationError, InvalidHashError):
        return False


# Si el correo no existe se verifica contra este hash, para tardar lo mismo
# y no revelar qué correos tienen cuenta.
HASH_FALSO = hashear(secrets.token_urlsafe(32))


def nueva_ficha() -> str:
    """Ficha secreta de 32 bytes (sesión o invitación). Nunca se guarda tal cual."""
    return secrets.token_urlsafe(32)


def huella(texto: str) -> str:
    """sha256 en hexadecimal: lo único que se guarda de una ficha."""
    return hashlib.sha256(texto.encode("utf-8")).hexdigest()
