# retos/

Aquí va **tu trabajo** en los retos de cada fase (los enunciados viven en `estudio/retos/`).

| Carpeta | Qué hay |
|---|---|
| `herramientas/` | Scripts comunes: preparar el entorno, ensamblar y trazar |
| `fase-1/` | Reto de cierre de Fase 1: «Del trazado a la ejecución» (Assembly x86-64) |

Los ejecutables se generan en `<carpeta>/build/`, que no se versiona.

## Herramientas

| Script | Para qué |
|---|---|
| `herramientas/preparar-entorno.sh` | Instala y verifica `nasm`, `ld` y `gdb` (x86-64). En la nube lo corre el script de preparación; en el escritorio, haz primero la mini-tarea 1 a mano. |
| `herramientas/ensamblar.sh programa.asm` | Ensambla (`nasm -f elf64 -g`) y enlaza (`ld`). Deja `build/programa`. |
| `herramientas/trazar.sh programa.asm [--pasos N] [--mem etiqueta]` | Ejecuta instrucción por instrucción y muestra, por paso: el renglón, ZF y solo lo que cambió (registros, memoria, saltos). Si la CPU se detiene por una señal (p. ej. `SIGSEGV`), lo dice. |

## Regla de estudio

**Predice primero, verifica después.** Antes de correr `trazar.sh`, escribe tu trazado (qué registro
cambia en cada paso, qué vale ZF, si el salto se toma). El script es para comprobar, no para descubrir.

## Escritorio o teléfono

- **Escritorio (WSL):** tú corres los comandos y usas `gdb` interactivo (es parte del reto).
- **Teléfono (Claude Code en la nube):** escribes el Assembly en el chat o lo dictas; el Tutor lo guarda,
  lo ensambla y corre `trazar.sh` cuando se lo pidas, y te muestra la salida tal cual.
