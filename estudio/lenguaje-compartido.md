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

## Verbos

| Verbo | En el taller |
|---|---|
| `mov` | traer una pieza del almacén a la mesa, o devolverla |
| `cmp` | medir dos piezas y anotar el resultado en la libreta, sin cortar nada |
| `jmp` | mover el dedo a otro renglón, siempre |
| `je` | mirar la libreta; mover el dedo solo si dice que coincidieron |

## Lo que la metáfora vuelve evidente

- La hoja también vive en el almacén: hoja y piezas compiten por el mismo camino. **Eso es von Neumann.**
- El carpintero nunca lee la hoja completa: lee un renglón, lo ejecuta y mira el siguiente. No sabe que
  existe un bucle; solo sabe que a veces el dedo va hacia atrás.
- Lo caro es ir al almacén, no cargar: por eso cada viaje trae 64 bytes (línea de caché).

**En una línea:** el carpintero lee la hoja con un dedo (`rip`), trabaja en la mesa (registros), anota en
la libreta (`rflags`), guarda copias en la repisa (caché), y todo —hoja, piezas y pila— vive en el
almacén (RAM).
