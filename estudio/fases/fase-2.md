# Fase 2 — El lenguaje del sistema: C · plan de fase (EN CURSO)

> Fuente: `estudio/plan-general.md` (no hay Prompt Maestro de Fase 2). Redactado por el Tutor el
> 2026-11-23 al cerrar la Fase 1; aprobado por el estudiante el mismo día. Base: `estudio/reportes/fase-1-cierre.md` (§7.4, §8 y Apéndice B).

**Objetivo:** pasar de ver la máquina a darle órdenes con nombre. C pone nombre a lo que la Fase 1 hacía
a mano: los estantes se vuelven punteros, los huecos de la mesa se vuelven variables con tamaño fijo y la
pila de hojas se vuelve la llamada a función. Al final, que la memoria manual y su primer fallo de
seguridad (el buffer overflow) se entiendan desde abajo.

**Temas, en orden estricto:**
1. **De C a Assembly:** compilar con `gcc`, leer la salida con `gcc -S -O0` y `objdump`. Un programa de
   C es una hoja que otro (el compilador) escribe por ti.
2. **Tipos y tamaños:** `char`, `int`, `long`, con y sin signo. Cada tipo es ℤ/2ⁿℤ con una
   interpretación. Overflow y conversiones, en conexión con SF, CF y OF.
3. **Punteros:** `&` y `*` como el número de estante y el viaje al estante. Aritmética de punteros
   (`p + 1` avanza el tamaño del tipo, no un byte). Arreglos y cadenas como punteros (el `inc rsi` de
   la mini-tarea 5).
4. **Funciones y el stack frame:** `call`/`ret`, dirección de retorno, variables locales, `rbp`/`rsp`.
   Es el desarrollo de la semilla de §7.4.
5. **Memoria manual:** heap, `malloc`/`free`, fugas, *use-after-free*, doble `free`.
6. **Structs:** el producto cartesiano con disposición en memoria (*layout*, *padding*), punteros a
   struct y lista enlazada (cada nodo guarda el estante del siguiente).
7. **Primer contacto con buffer overflows:** un arreglo local sin control de límites sobrescribe una
   variable vecina y luego la dirección de retorno. Se hace en laboratorio (`-fno-stack-protector`,
   `-no-pie`) y se nombran las defensas (canario, NX, ASLR) sin profundizar: eso es Fase 3 y Fase 6.

**Criterio de salida:** escribe programas pequeños en C que manipulan memoria manualmente, y entiende qué
ocurre debajo: para un fragmento dado, dice qué Assembly produce a grandes rasgos y qué pasa en el stack
o en el heap.

**Metodología específica:**
- **Escritorio (WSL)** para escribir, compilar y depurar (`gcc`, `gdb`). **Teléfono** para cápsulas
  conceptuales y trazados.
- Cada tema nuevo de C se ancla en su Assembly de Fase 1: «¿qué hoja escribió el compilador?».
- Formato que funcionó en el reto de Fase 1: **ejemplo resuelto → ejercicio equivalente hecho solo**, y
  siempre **predice primero, verifica después**.
- Vigilar los gaps heredados: finitud (tema 2), dirección / contenido (tema 3), «el hardware se recupera
  solo» (temas 5 y 7), SF/CF (tema 2), disciplina de predicción.
- Anclas matemáticas: un tipo es un anillo finito con una interpretación; un puntero es un elemento del
  dominio de f: D → {0,1}⁸; un struct es un producto con coordenadas en posiciones fijas; `free` encoge
  el dominio de una función parcial que el programa sigue evaluando.
- Extender la metáfora del taller, sin reemplazarla: el compilador como escribano de hojas, el heap como
  estantes que el dueño presta y hay que devolver.

**Retos:**
- **Semanal** (30–45 min): un programa corto o un trazado C ↔ Assembly.
- **Quincenal** (integrador): p. ej. reescribir en C la mini-tarea 5 (sumar un arreglo con un puntero) y
  comparar su Assembly con el `mt5.asm` escrito a mano.
- **Reto de cierre de fase:** se redacta en `estudio/retos/fase-2-reto-cierre.md` al llegar al tema 7.
  Idea: lista enlazada en el heap sin fugas, más un overflow controlado observado en gdb.

**Transición:** C deja ver la memoria del proceso pero no a quien la administra. Cada `malloc`, cada
`printf` y cada fallo de segmento termina tocando la puerta del dueño: la Fase 3 (sistema operativo)
abre esa puerta.
