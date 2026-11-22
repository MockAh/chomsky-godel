# Progreso del estudiante

> Documento vivo. **Solo lo actualiza el Escriba**, al cierre de cada sesión, con base en lo que pasó en
> ella. No se inventa progreso: si algo no está registrado, se dice «sin registro».
> Fechas siempre absolutas (AAAA-MM-DD).

## Estado actual

- **Fase actual:** 1 — La máquina desnuda.
- **Criterio de salida de la fase:** cumplido en lo teórico (2026-10-04, trazados A.1 y A.2 del reporte de cierre).
- **Pendiente para cerrar la fase:** el **reto de cierre de escritorio** (`retos/fase-1-reto-cierre.md`):
  escribir, ensamblar y ejecutar Assembly x86-64 en WSL con nasm, ld y gdb.
  - Mini-tarea 1 (preparar el taller): **cumplida 2026-11-20** (nasm 2.16.01, ld 2.42, gdb 15.1, x86_64).
  - Mini-tarea 2 (primer programa verificable): **cumplida 2026-11-20** (`retos/fase-1/mt2.asm`; 42,
    300→44, 256→0, 511→255).
  - Mini-tarea 3 (traducir A.1): **cumplida 2026-11-22.** A.1 lo resolvió el Tutor con ayuda
    (2026-11-20); el ejercicio equivalente lo resolvió él solo en `retos/fase-1/mt3.asm` (predijo y
    verificó código 0; con `cmp rax, 14`, código 1).
  - Mini-tarea 4 (paso a paso en gdb): **cumplida 2026-11-22** (`starti`, `si`, `display`; trazado
    predicho y verificado sobre `mt3`).
  - Mini-tarea 5 (bucle con indirección, `retos/fase-1/mt5.asm`): sin empezar. Es la última del reto.
- **Siguiente sesión (pedido del estudiante, 2026-11-23):** mini-tarea 5. Al cumplirla, el Tutor propone
  el cierre de la Fase 1 (reporte de cierre + plan de Fase 2) para que el estudiante lo apruebe.
- **Siguiente fase:** 2 — El lenguaje del sistema: C. Su plan de fase (`fases/fase-2.md`) aún no existe;
  el Tutor lo redacta a partir de `plan-general.md` al abrir la fase, y el estudiante lo aprueba.
- **Nivel de dificultad actual:** alto dentro de Fase 1 (traza Assembly con indirección).

## Fases cerradas

| Fase | Cierre | Reporte |
|---|---|---|
| 0 — El puente | Criterio cumplido (fecha sin registro) | `reportes/fase-0-cierre.md` |

## Dudas abiertas y gaps detectados

- **La finitud** (gap central como matemático): registros contados, memoria finita, costo por ciclo.
  Seguir reforzándolo en Fase 2 (tamaños de tipos, overflow, memoria manual).
- **Intuición de «el hardware se recupera solo»:** ante `rip` desalineado respondió que el procesador
  detectaría el desfase (Fase 1, ejercicio conceptual 4). Corregido; vigilarlo en buffer overflows.
- **Escribir ramas desde cero** (2026-11-20): aún no lo lograba solo; pidió la solución de A.1 en código.
  Avance 2026-11-22: con el ejemplo resuelto delante, escribió solo un programa con dos ramas. Falta verlo
  sin modelo (mini-tarea 5).
- **Qué instrucciones escriben en la libreta** (2026-11-22): creía que solo `cmp` deja marcas; corregido
  (`sub` también; `mov` y `je` no). Verificarlo en el bucle de la mini-tarea 5.
- **«?» en registros sin asignar** (2026-11-22): misma raíz que la finitud: en la máquina todo bit tiene
  valor (al arrancar, Linux deja los registros en 0).
- **SF y CF** (2026-11-22): no supo qué marca enciende un resultado negativo; explicado (SF = 1, CF = 1 en
  14 − 15), sin ejercicio propio todavía.
- **Disciplina de predicción** (2026-11-22): en un extra corrió antes de predecir; señalado.
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

## Registro de sesiones

Ver `sesiones/` (una nota por sesión, escrita por el Escriba). Antes de 2026-11-07 el registro vivía en
documentos sueltos: ver `reportes/` y `notas/`.
