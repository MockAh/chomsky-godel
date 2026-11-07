#!/usr/bin/env bash
# Ejecuta un programa NASM instrucción por instrucción y muestra qué cambió en cada paso.
# Pensado para el teléfono, donde no hay gdb interactivo. En el escritorio, usa gdb directamente.
#
#   retos/herramientas/trazar.sh programa.asm [--pasos N] [--mem etiqueta]...
#
#   --pasos N        máximo de instrucciones a ejecutar (por defecto 60)
#   --mem etiqueta   muestra la palabra de 8 bytes en esa etiqueta de .data cuando cambie
#
# Regla de estudio: escribe tu predicción del trazado ANTES de correr esto.
set -euo pipefail
aqui=$(cd "$(dirname "$0")" && pwd)
[ $# -ge 1 ] || { echo "Uso: $0 programa.asm [--pasos N] [--mem etiqueta]..." >&2; exit 2; }
asm=$1; shift
pasos=60; mem=()
while [ $# -gt 0 ]; do
  case "$1" in
    --pasos) pasos=$2; shift 2 ;;
    --mem) mem+=("$2"); shift 2 ;;
    *) echo "Opción desconocida: $1" >&2; exit 2 ;;
  esac
done
exe=$("$aqui/ensamblar.sh" "$asm")
TRAZA_PASOS=$pasos TRAZA_MEM=$(IFS=,; echo "${mem[*]:-}") \
  gdb -q -nx -batch -x "$aqui/trazar.py" --args "$exe" 2>&1 | grep -v -E '^(warning: Error disabling address space randomization|Program stopped\.|Program received signal|Program terminated with signal|The program no longer exists|^$|\[Inferior [0-9]+ \(process [0-9]+\) exited)'
