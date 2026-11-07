# Reto de cierre · Fase 1 — «Del trazado a la ejecución»

Enunciado: `estudio/retos/fase-1-reto-cierre.md`. Progreso: `estudio/progreso.md`.

| Mini-tarea | Tu archivo | Estado |
|---|---|---|
| 1 · Preparar el taller | — (comandos en la terminal) | ver `progreso.md` |
| 2 · Primer programa verificable | `mt2.asm` | |
| 3 · Traducir el trazado A.1 a código real | `mt3.asm` | |
| 4 · Ejecutar paso a paso viendo los registros | `mt3.asm` en `gdb` | |
| 5 · Bucle con indirección | `mt5.asm` | |

Los `.asm` los escribes tú: aquí no hay soluciones.

```bash
retos/herramientas/ensamblar.sh retos/fase-1/mt2.asm      # → retos/fase-1/build/mt2
./retos/fase-1/build/mt2; echo "código de salida: $?"
retos/herramientas/trazar.sh retos/fase-1/mt3.asm         # trazado verificable
```

## gdb, referencia mínima (escritorio)

| Comando | Qué hace |
|---|---|
| `gdb -q retos/fase-1/build/mt3` | Abre el programa sin correrlo |
| `starti` | Arranca y se detiene **antes** de la primera instrucción |
| `si` | Ejecuta **una** instrucción (*step instruction*) |
| `info registers rax rbx rcx rip eflags` | Muestra esos registros |
| `x/gx &etiqueta` | Muestra 8 bytes de memoria en esa etiqueta, en hexadecimal |
| `layout regs` | Vista dividida: código + registros (sal con `tui disable`) |
