#!/usr/bin/env bash
# Instala y verifica el taller de Assembly: nasm, ld (binutils) y gdb.
# Sirve para la nube (script de preparación de Claude Code) y para el escritorio.
# En el escritorio, la mini-tarea 1 del reto de Fase 1 es hacer esto a mano: hazla primero.
set -euo pipefail

arq=$(uname -m)
if [ "$arq" != "x86_64" ]; then
  echo "Arquitectura $arq: el reto de Fase 1 es x86-64. Avísale al Tutor." >&2
  exit 1
fi

faltan=()
for h in nasm ld gdb; do command -v "$h" >/dev/null || faltan+=("$h"); done
if [ ${#faltan[@]} -gt 0 ]; then
  echo "Instalando: nasm binutils gdb"
  pref=""; [ "$(id -u)" -ne 0 ] && pref="sudo"
  $pref apt-get update -qq
  $pref apt-get install -y -qq nasm binutils gdb >/dev/null
fi

echo "arquitectura: $arq"
nasm -v
ld -v
gdb --version | head -1
