"""Visibilidad y exportación de anotaciones (spec 02 §4 y 03 §5).

Hacia afuera el autor se muestra por su rol, nunca por su correo.
"""
from __future__ import annotations

import time

from .seguridad import huella

ROL_VISIBLE = {"admin": "Admin", "tester": "Tester"}
TIPOS_ELEMENTO = ("ejercicio", "circuito", "pregunta", "lectura")


def clave_elemento(seccion: str, titulo: str) -> str:
    return huella(f"{seccion}|{titulo}")[:16]


def publica(nota: dict) -> dict:
    """Quita `autor` y `rol`; agrega `autor_rol`."""
    n = {k: v for k, v in nota.items() if k not in ("autor", "rol")}
    n["autor_rol"] = ROL_VISIBLE.get(nota["rol"], nota["rol"].capitalize())
    return n


def vigentes(temas: list[dict]) -> dict[tuple[str, str], str]:
    """(tema, pestaña) → sha256 del archivo publicado hoy."""
    return {(t["id"], p["id"]): p["sha256"] for t in temas for p in t["pestanas"]}


def visibles(notas: list[dict], correo: str, es_admin: bool, hashes: dict) -> dict:
    mias, mias_elementos, anteriores, de_otros = [], [], [], []
    for n in notas:
        vigente = hashes.get((n["tema"], n["pestana"])) == n["version_hash"]
        if n["autor"] == correo:
            if vigente:
                (mias_elementos if n["elemento"] else mias).append(publica(n))
            elif n["texto"].strip():
                anteriores.append(publica(n))
        elif es_admin and n["texto"].strip():
            de_otros.append(publica(n))
    anteriores.sort(key=lambda n: n["actualizada"], reverse=True)
    de_otros.sort(key=lambda n: n["actualizada"], reverse=True)
    grupos = {"mias": mias, "mias_elementos": mias_elementos, "anteriores": anteriores}
    if es_admin:
        grupos["de_otros"] = de_otros
    return grupos


def _fecha(segundos: float) -> str:
    return time.strftime("%Y-%m-%d %H:%M UTC", time.gmtime(segundos))


def a_markdown(notas: list[dict], manifiesto: dict, ahora: float) -> str:
    """Todas las notas no vacías, ordenadas por tema, pestaña y sección del manifiesto."""
    temas = manifiesto["temas"]
    orden_tema = {t["id"]: i for i, t in enumerate(temas)}
    info = {t["id"]: t for t in temas}
    hashes = vigentes(temas)

    def nombre_tema(tid):
        return info[tid]["nombre"] if tid in info else f"{tid} (retirado)"

    def etiqueta_pestana(tid, pid):
        for p in info.get(tid, {}).get("pestanas", []):
            if p["id"] == pid:
                return p["etiqueta"]
        return f"{pid} (retirada)"

    def nombre_seccion(tid, sid):
        for s in info.get(tid, {}).get("secciones", []):
            if s["id"] == sid:
                return s["nombre"]
        return sid

    def posicion(lista, clave, valor):
        ids = [x[clave] for x in lista]
        return ids.index(valor) if valor in ids else len(ids)

    def orden(n):
        t = info.get(n["tema"], {})
        return (orden_tema.get(n["tema"], len(temas)), n["tema"],
                posicion(t.get("pestanas", []), "id", n["pestana"]), n["pestana"],
                posicion(t.get("secciones", []), "id", n["seccion"]), n["seccion"],
                n["elemento"] is not None, (n["elemento"] or {}).get("titulo", ""),
                -n["actualizada"])

    lineas = ["# Anotaciones · chomsky-godel", "",
              f"Exportado: {_fecha(ahora)} · contenido `{manifiesto.get('commit', '')}`", ""]
    tema_actual = grupo_actual = None
    for n in sorted((n for n in notas if n["texto"].strip()), key=orden):
        if n["tema"] != tema_actual:
            tema_actual, grupo_actual = n["tema"], None
            lineas += [f"## {nombre_tema(n['tema'])}", ""]
        grupo = (n["pestana"], n["seccion"])
        if grupo != grupo_actual:
            grupo_actual = grupo
            lineas += [f"### {etiqueta_pestana(n['tema'], n['pestana'])} · "
                       f"{nombre_seccion(n['tema'], n['seccion'])}", ""]
        p = publica(n)
        if n["elemento"]:
            e = n["elemento"]
            detalle = ", ".join(x for x in (e.get("tipo"), e.get("estado")) if x)
            lineas += [f"#### {e['titulo']}" + (f" ({detalle})" if detalle else ""), ""]
        vigente = "vigente" if hashes.get((n["tema"], n["pestana"])) == n["version_hash"] else "versión anterior"
        lineas += [f"**{p['autor_rol']}** · {n['version']} ({vigente}) · {_fecha(n['actualizada'])}", "",
                   n["texto"].strip(), "", "---", ""]
    if tema_actual is None:
        lineas += ["_Todavía no hay anotaciones._", ""]
    return "\n".join(lineas)
