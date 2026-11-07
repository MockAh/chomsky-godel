#!/usr/bin/env bash
# Ensambla y enlaza un programa NASM x86-64 (Linux, sin libc).
#   retos/herramientas/ensamblar.sh retos/fase-1/mi-programa.asm
# Deja el ejecutable en <carpeta>/build/<nombre> y lo imprime. Con -g: símbolos para gdb.
set -euo pipefail
[ $# -eq 1 ] || { echo "Uso: $0 programa.asm" >&2; exit 2; }
asm=$1
[ -f "$asm" ] || { echo "No existe: $asm" >&2; exit 2; }
dir=$(dirname "$asm"); nombre=$(basename "$asm" .asm)
mkdir -p "$dir/build"
nasm -f elf64 -g -F dwarf -o "$dir/build/$nombre.o" "$asm"
ld -o "$dir/build/$nombre" "$dir/build/$nombre.o"
echo "$dir/build/$nombre"
