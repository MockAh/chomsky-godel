# Lenguaje compartido: la metáfora del taller

> Construida en la Fase 1 (`reportes/fase-1-cierre.md` §10, `notas/fase-1/sintesis-carpintero-21-09.md`,
> `notas/fase-1/alu-y-unidad-de-control.md`). **Conservarla en las fases siguientes**: tutores, mapas y
> lecciones del sitio la usan como vocabulario común. Extenderla, no reemplazarla.

## Piezas

| En el taller | En la máquina |
|---|---|
| El **Maestro Mayor** (capataz): lee la orden, la descifra y grita qué hacer | Unidad de Control |
| El **Carpintero** (oficial de banco): transforma lo que hay en la mesa | ALU |
| (Juntos, «el carpintero» en la versión simple) | UC + ALU |
| El taller completo | CPU |
| La hoja de instrucciones | El código del programa, en memoria |
| El dedo sobre el renglón | `rip` |
| La mano que sostiene el renglón | Registro de instrucción (IR), invisible al programador |
| Los 16 huecos de la mesa | Registros de propósito general (16 × 8 bytes = 128 bytes) |
| La libreta al margen | `rflags` (en Fase 1: ZF) |
| La repisa pegada a la mesa | Caché L1 (separada: hoja = L1i, piezas = L1d) |
| Las estanterías de la habitación | Caché L2 y L3 (mixtas) |
| El almacén | RAM |
| La bodega lejana | Disco (nada se ejecuta desde ahí) |
| Las piezas | Los datos |
| La pila de hojas boca abajo | Stack |
| La marca sobre la hoja de encima | `rsp` |
| La campana del taller | Reloj |
| El ayudante que elige el segundo tablón (¿de la mesa o escrito en la hoja?) | MUX de operando (registro / inmediato) |
| El ayudante que elige qué se deja en la mesa | MUX de escritura (writeback) |
| El **dueño del taller**: decide qué hoja entra, asigna estantes, pone el dedo en el primer renglón y cierra el taller (2026-11-20) | Sistema operativo |
| **Tocar la puerta del dueño** (2026-11-20) | `syscall` |
| El **número de trámite** / el **dato del trámite** (2026-11-20) | `rax` (60 = terminar) / `rdi` (código de salida) |
| La **nota al margen** de un renglón (2026-11-20) | Etiqueta (`_start:`, `iguales:`); nasm la cambia por un número |
| El **número de estante** de un renglón (2026-11-20) | Dirección en memoria (p. ej. `0x401000`) |
| Más marcas en la libreta (2026-11-20) | SF, CF, OF además de ZF |
| La **lista de marcas encendidas** de la libreta (2026-11-22) | Los corchetes de `$eflags` en gdb, p. ej. `[ PF ZF IF ]`; lo que no aparece vale 0 |
| La **marca del dueño** (2026-11-22) | IF: la pone el SO («el taller acepta interrupciones»), no una cuenta |

## Verbos

| Verbo | En el taller |
|---|---|
| `mov` | traer una pieza del almacén a la mesa, o devolverla |
| `cmp` | medir dos piezas y anotar el resultado en la libreta, sin cortar nada |
| `jmp` | mover el dedo a otro renglón, siempre |
| `je` | mirar la libreta; mover el dedo solo si dice que coincidieron |
| `syscall` | tocar la puerta del dueño; él lee la mesa (`rax`, `rdi`) y hace el trámite (2026-11-20) |
| derramarse | un bloque sin salto ni `syscall` cae en el renglón siguiente (2026-11-20) |
| escribir en la libreta | lo hacen las cuentas del Carpintero (`sub`, `cmp`); traer piezas (`mov`) y mirar la libreta (`je`) no (2026-11-22) |

## Lo que la metáfora vuelve evidente

- La hoja también vive en el almacén: hoja y piezas compiten por el mismo camino. **Eso es von Neumann.**
- El carpintero nunca lee la hoja completa: lee un renglón, lo ejecuta y mira el siguiente. No sabe que
  existe un bucle; solo sabe que a veces el dedo va hacia atrás.
- Lo caro es ir al almacén, no cargar: por eso cada viaje trae 64 bytes (línea de caché).
- **La máquina no tiene «?»** (2026-11-22): cada hueco de la mesa y cada marca de la libreta siempre valen
  algo; al abrir el taller, el dueño los deja en 0.

**En una línea:** el carpintero lee la hoja con un dedo (`rip`), trabaja en la mesa (registros), anota en
la libreta (`rflags`), guarda copias en la repisa (caché), y todo —hoja, piezas y pila— vive en el
almacén (RAM).
