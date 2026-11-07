"""Script de gdb (lo llama trazar.sh): ejecuta paso a paso y reporta solo lo que cambia.

Columnas: paso · instrucción ejecutada · ZF (con * si cambió) · efectos (registros, otras banderas,
memoria, salto).
"""
import os

import gdb

REGS = ["rax", "rbx", "rcx", "rdx", "rsi", "rdi", "rbp", "rsp",
        "r8", "r9", "r10", "r11", "r12", "r13", "r14", "r15"]
BANDERAS = {"CF": 0, "ZF": 6, "SF": 7, "OF": 11}
PASOS = int(os.environ.get("TRAZA_PASOS", "60"))
MEM = [m for m in os.environ.get("TRAZA_MEM", "").split(",") if m]


def valor(v):
    v &= (1 << 64) - 1
    if v < 1 << 32:
        return str(v)
    if v >= 1 << 63 and v - (1 << 64) > -(1 << 31):  # negativo pequeño en complemento a dos
        return f"{v - (1 << 64)} (0x{v:x})"
    return f"0x{v:x}"


SENALES = {
    "SIGSEGV": "acceso a memoria no permitido; el sistema operativo detuvo el programa",
    "SIGILL": "instrucción inválida: esos bytes no son un opcode que la CPU sepa ejecutar",
    "SIGFPE": "error aritmético (p. ej. división entre cero)",
    "SIGBUS": "acceso a memoria mal alineado o inexistente",
}
_senal = []


def _al_detenerse(evento):
    if isinstance(evento, gdb.SignalEvent) and evento.stop_signal != "SIGTRAP":
        _senal.append(evento.stop_signal)


def vivo():
    return gdb.selected_inferior().pid != 0


def foto():
    f = gdb.selected_frame()
    r = {n: int(f.read_register(n)) & ((1 << 64) - 1) for n in REGS}
    fl = int(f.read_register("eflags"))
    r.update({b: (fl >> bit) & 1 for b, bit in BANDERAS.items()})
    inf = gdb.selected_inferior()
    for m in MEM:
        dir_ = int(gdb.parse_and_eval(f"(long)&{m}"))
        r[f"[{m}]"] = int.from_bytes(bytes(inf.read_memory(dir_, 8)), "little")
    return r


_fuentes = {}


def instruccion(pc):
    """El renglón tal como lo escribió el estudiante (sin etiqueta ni comentario); si no hay, el desensamblado."""
    d = gdb.selected_frame().architecture().disassemble(pc)[0]
    texto = d["asm"].split("#")[0].strip()
    sal = gdb.find_pc_line(pc)
    if sal.symtab and sal.line:
        ruta = sal.symtab.fullname()
        if ruta not in _fuentes:
            try:
                _fuentes[ruta] = open(ruta, encoding="utf-8").read().splitlines()
            except OSError:
                _fuentes[ruta] = []
        lineas = _fuentes[ruta]
        if 0 < sal.line <= len(lineas):
            renglon = lineas[sal.line - 1].split(";")[0]
            if ":" in renglon.split()[0] if renglon.split() else False:
                renglon = renglon.split(":", 1)[1]
            renglon = " ".join(renglon.split())
            if renglon:
                texto = renglon
    return texto, d["length"]


def simbolo(v):
    """Si v es la dirección de una etiqueta del programa, su nombre."""
    if v < 0x400000 or v >= 1 << 47:
        return None
    info = gdb.execute(f"info symbol {v}", to_string=True)
    if info.startswith("No symbol"):
        return None
    nombre = info.split(" in section")[0].strip()
    return None if "+" in nombre else nombre


def mostrar(k, v):
    s = simbolo(v) if k in REGS else None
    return f"{k}=0x{v:x} = &{s}" if s else f"{k}={valor(v)}"


def principal():
    gdb.execute("set pagination off")
    gdb.execute("set disassembly-flavor intel")
    gdb.execute("set disable-randomization on", to_string=True)
    gdb.execute("set suppress-cli-notifications on")
    gdb.execute("set print frame-info short-location", to_string=True)
    gdb.execute("starti", to_string=True)
    gdb.events.stop.connect(_al_detenerse)
    antes = foto()
    print(f"inicio: rsp={valor(antes['rsp'])}" + "".join(f"  {k}={valor(v)}" for k, v in antes.items() if k.startswith("[")))
    print(f"{'paso':>4}  {'instrucción':<24} ZF  efectos")
    for paso in range(1, PASOS + 1):
        pc = int(gdb.parse_and_eval("$pc"))
        texto, largo = instruccion(pc)
        gdb.execute("stepi", to_string=True)
        if _senal:
            nombre = _senal[0]
            print(f"{paso:>4}  {texto:<24} {'':2}  ✖ {nombre}: {SENALES.get(nombre, 'señal del sistema operativo')}")
            return
        if not vivo():
            codigo = gdb.parse_and_eval("$_exitcode")
            print(f"{paso:>4}  {texto:<24} {'':2}  fin del programa · código de salida {int(codigo)}")
            return
        ahora = foto()
        efectos = [mostrar(k, v) for k, v in ahora.items() if v != antes.get(k) and k not in BANDERAS]
        efectos += [f"{k}={v}" for k, v in ahora.items() if k in BANDERAS and k != "ZF" and v != antes[k]]
        nuevo_pc = int(gdb.parse_and_eval("$pc"))
        if nuevo_pc != pc + largo:
            destino = gdb.execute(f"info symbol {nuevo_pc}", to_string=True).split(" in section")[0]
            efectos.append(f"SALTA → {destino.replace(' + ', '+')}")
        zf = f"{ahora['ZF']}{'*' if ahora['ZF'] != antes['ZF'] else ' '}"
        print(f"{paso:>4}  {texto:<24} {zf}  {'  '.join(efectos) or '—'}")
        antes = ahora
    print(f"(se detuvo tras {PASOS} pasos; usa --pasos para más)")


try:
    principal()
except gdb.error as e:
    print(f"gdb: {e}")
