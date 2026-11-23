# Fase 1 — La máquina desnuda · plan de fase (CERRADA)

> Fuente: `Prompt_Maestro_3_Fase_1`. Reporte de cierre: `estudio/reportes/fase-1-cierre.md`.

**Objetivo:** conectar la lógica booleana de la Fase 0 con la máquina física real. Entender qué ocurre
dentro de una CPU instrucción por instrucción, y cómo la memoria organiza y mueve los datos. La Máquina de
Turing abstracta se vuelve silicio concreto.

**Temas, en orden estricto:**
1. Arquitectura de CPU: la ALU como ejecutora de operaciones booleanas y aritméticas. Registros como
   memoria ultra-rápida y finita.
2. El ciclo fetch-decode-execute: el «paso de cómputo» real, análogo a la transición de estado de la MT.
3. Organización de la memoria: RAM, jerarquía de caché, y la distinción crítica entre stack y heap.
4. Direccionamiento: qué es una dirección, cómo se referencia un dato (cimiento de los punteros de Fase 2).
5. Assembly x86 básico: registros, `mov`, aritmética, saltos y comparaciones. Leer y trazar, aún no
   escribir programas complejos.

**Criterio de salida:** lee un fragmento de Assembly x86 básico y traza mentalmente, paso a paso, qué hace
la CPU y cómo cambian los registros y la memoria.

**Metodología específica:**
- El salto conceptual es **la finitud**: registros contados, memoria limitada, cada instrucción cuesta
  ciclos. Reforzarlo constantemente: es el gap central del estudiante como matemático.
- Anclar en la Máquina de Turing: fetch-decode-execute es la materialización de δ; la cinta infinita se
  vuelve memoria finita y direccionable. Hacer explícita la correspondencia.
- Assembly se introduce **leyendo**, no escribiendo: primero trazar código existente. Escribir viene
  después, en desktop.
- **Reto semanal:** trazado o pequeño programa en Assembly (Termux o emulador), 30–45 min.
- **Reto quincenal:** integrador; p. ej. traducir una operación matemática simple a Assembly y verificar
  su ejecución registro por registro.
- **Transición:** esta fase prepara C. Al explicar memoria y direccionamiento, sembrar deliberadamente la
  intuición que hará clic con los punteros.
