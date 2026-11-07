# Reto de cierre — Fase 1: «Del trazado a la ejecución»

Cinco mini-tareas de unos 15 minutos. Escribir Assembly x86-64 real, ensamblarlo, ejecutarlo y verlo
correr instrucción por instrucción en un depurador. WSL es mejor entorno que Termux: es x86-64 nativo,
justo la arquitectura estudiada.

**El arco:** (1) preparar el taller → (2) primer programa verificable → (3) traducir el trazado A.1 a
código real → (4) ejecutar paso a paso viendo los registros → (5) bucle con indirección.

## Mini-tarea 1 — Preparar el taller

**Objetivo:** tener `nasm`, `ld` y `gdb` funcionando, y confirmar que se está en x86-64 de verdad.

```bash
uname -m            # debe responder x86_64 (si dice aarch64, cambia todo el reto)
sudo apt update
sudo apt install -y nasm binutils gdb
nasm -v
ld -v
gdb --version
mkdir -p ~/fase1 && cd ~/fase1 && pwd
```

- `nasm` — el ensamblador: traduce el Assembly a bytes de máquina.
- `binutils` — trae `ld`, el enlazador, que empaqueta esos bytes en un ejecutable.
- `gdb` — el depurador: deja detener la CPU y mirar los registros.

**Criterio de terminación:** las tres herramientas responden con su versión y `pwd` devuelve algo
como `/home/<usuario>/fase1`.

## Mini-tareas 2 a 5

Solo están definidas por su título en el arco de arriba. El Tutor las desarrolla una por una cuando
llegue el momento (ver `estudio/progreso.md`).
