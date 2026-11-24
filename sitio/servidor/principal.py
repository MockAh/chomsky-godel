"""Entrada en Cloud Run (spec 02 §2): la app con el almacén en Firestore.

    uvicorn servidor.principal:app

El cliente de Firestore toma el proyecto y las credenciales del entorno (la cuenta
de servicio de Cloud Run). El contenido es la carpeta que arma armar_contenido.py.
"""
from pathlib import Path

from .almacen_firestore import AlmacenFirestore
from .app import crear_app

app = crear_app(AlmacenFirestore(), Path(__file__).resolve().parent.parent / "contenido")
