# Progreso del estudiante

> Documento vivo. **Solo lo actualiza el Escriba**, al cierre de cada sesión, con base en lo que pasó en
> ella. No se inventa progreso: si algo no está registrado, se dice «sin registro».
> Fechas siempre absolutas (AAAA-MM-DD).

## Estado actual

- **Fase actual:** 2 — El lenguaje del sistema: C. Plan aprobado el 2026-11-23 (`fases/fase-2.md`).
- **Último tema:** ninguno de Fase 2 todavía.
- **Siguiente sesión:** Fase 2, tema 1 (de C a Assembly: `gcc -S -O0`, `objdump`). Escritorio (WSL) para
  compilar; requiere `gcc` (verificar que esté instalado).
- **Nivel de dificultad actual:** alto al cierre de Fase 1 (escribe solo un bucle con indirección).

## Fases cerradas

| Fase | Cierre | Reporte |
|---|---|---|
| 0 — El puente | Criterio cumplido (fecha sin registro) | `reportes/fase-0-cierre.md` |
| 1 — La máquina desnuda | Teoría 2026-10-04; reto de escritorio 2026-11-23; cierre aprobado 2026-11-23 | `reportes/fase-1-cierre.md` (Apéndice B: las 5 mini-tareas) |

### Registro de Fase 1: reto de cierre de escritorio (`retos/fase-1-reto-cierre.md`)

- Mini-tarea 1 (preparar el taller): cumplida 2026-11-20 (nasm 2.16.01, ld 2.42, gdb 15.1, x86_64).
- Mini-tarea 2 (primer programa verificable): cumplida 2026-11-20 (`retos/fase-1/mt2.asm`).
- Mini-tarea 3 (traducir A.1): cumplida 2026-11-22 (`retos/fase-1/mt3.asm`, ejercicio equivalente solo).
- Mini-tarea 4 (paso a paso en gdb): cumplida 2026-11-22.
- Mini-tarea 5 (bucle con indirección): cumplida 2026-11-23 (`retos/fase-1/mt5.asm`, solo; código 18).

## Dudas abiertas y gaps detectados

### Para vigilar en Fase 2

- **Estante vs. pieza (dirección vs. contenido)** (2026-11-23): en la mini-tarea 5 ignoró los `inc` y luego
  sumó a la pieza en vez de al estante. Lo resolvió con direcciones concretas en hexadecimal. Clave para
  punteros (Fase 2, tema 3).
- **Lectura de ZF** (2026-11-23): la lee como «son iguales» aun tras `dec`; matizado: «la última cuenta dio 0».
- Siguen abiertos de Fase 1: finitud, «el hardware se recupera solo», SF y CF sin ejercicio propio.

### Registro de Fase 1

- **La finitud** (gap central como matemático): registros contados, memoria finita, costo por ciclo.
  Seguir reforzándolo en Fase 2 (tamaños de tipos, overflow, memoria manual).
- **Intuición de «el hardware se recupera solo»:** ante `rip` desalineado respondió que el procesador
  detectaría el desfase (Fase 1, ejercicio conceptual 4). Corregido; vigilarlo en buffer overflows.
- **Escribir ramas desde cero** (2026-11-20): aún no lo lograba solo; pidió la solución de A.1 en código.
  Avance 2026-11-22: con el ejemplo resuelto delante, escribió solo un programa con dos ramas.
  **Resuelto 2026-11-23:** escribió solo el bucle con indirección a partir de un ejemplo sin indirección.
- **Qué instrucciones escriben en la libreta** (2026-11-22): creía que solo `cmp` deja marcas; corregido
  (`sub` también; `mov` y `je` no). **Resuelto 2026-11-23:** vio en la traza que `dec` enciende ZF.
- **«?» en registros sin asignar** (2026-11-22): misma raíz que la finitud: en la máquina todo bit tiene
  valor (al arrancar, Linux deja los registros en 0).
- **SF y CF** (2026-11-22): no supo qué marca enciende un resultado negativo; explicado (SF = 1, CF = 1 en
  14 − 15), sin ejercicio propio todavía.
- **Disciplina de predicción** (2026-11-22): en un extra corrió antes de predecir; señalado. En la
  mini-tarea 5 (2026-11-23) predijo antes de correr.
- **Finitud, avance** (2026-11-20): predijo 300→300; tras la explicación razonó solo en ℤ/256ℤ
  (256→0, 511→255).
- **Resueltos 2026-11-20:** separación hoja / mesa / libreta; etiqueta = dirección (número de estante).
- **Resueltos 2026-11-22:** semántica de `je` (la predijo y usó bien solo); lectura de `$eflags` en gdb
  (los corchetes = marcas en 1, el soporte f⁻¹(1)).

## Observaciones de los tutores

- Responde mejor con metáforas físicas sostenidas (el grifo, el taller) que con densidad técnica sin ancla;
  ver `lenguaje-compartido.md`.
- Las correspondencias formales (MT ↔ CPU, memoria como función f: D → {0,1}⁸, F(F(x)) como indirección)
  le dan intuición inmediata: usarlas.
- En el reto de escritorio (2026-11-20) aprende mejor con un ejemplo resuelto primero y luego un ejercicio
  equivalente que hace solo. Los desensamblados reales (`objdump`) le aclararon que las etiquetas son números.
- Ese formato funcionó (2026-11-22): resolvió solo el ejercicio equivalente. Ver la salida real de gdb
  contra su predicción, en tabla, le resultó claro; la lectura como conjunto (f⁻¹(1)) le resolvió los
  corchetes de `eflags`.

- Fase 1, mini-tarea 5 (2026-11-23): un ejemplo que **no** contiene la parte nueva (bucle sin indirección)
  lo obligó a integrar solo; funcionó. Las direcciones concretas en hex (`0x402000` → 5) le aclararon
  estante vs. pieza mejor que `piezas + k`.

## Registro de sesiones

Ver `sesiones/` (una nota por sesión, escrita por el Escriba). Antes de 2026-11-07 el registro vivía en
documentos sueltos: ver `reportes/` y `notas/`.
