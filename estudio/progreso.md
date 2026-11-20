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
  - Mini-tarea 3 (traducir A.1): **empezada 2026-11-20.** A.1 resuelto por el Tutor con ayuda; pendiente
    el ejercicio equivalente (20, 6, `cmp rax, 15`) que él resuelve solo en `retos/fase-1/mt3.asm`.
  - Mini-tareas 4 y 5: sin empezar.
- **Siguiente sesión (pedido del estudiante):** empezar mostrándole el A.1 resuelto y el ejercicio que le
  toca resolver solo; ambos en `sesiones/2026-11-20-reto-f1-mt1-mt2.md` §3.2 y §3.3.
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
- **Semántica de `je` invertida** (2026-11-20): creía que salta cuando *no* da cero. Corregido; verificar
  en el ejercicio equivalente de la mini-tarea 3.
- **Escribir ramas desde cero** (2026-11-20): aún no lo logra solo; pidió la solución de A.1 en código.
- **Finitud, avance** (2026-11-20): predijo 300→300; tras la explicación razonó solo en ℤ/256ℤ
  (256→0, 511→255).
- **Resueltos 2026-11-20:** separación hoja / mesa / libreta; etiqueta = dirección (número de estante).

## Observaciones de los tutores

- Responde mejor con metáforas físicas sostenidas (el grifo, el taller) que con densidad técnica sin ancla;
  ver `lenguaje-compartido.md`.
- Las correspondencias formales (MT ↔ CPU, memoria como función f: D → {0,1}⁸, F(F(x)) como indirección)
  le dan intuición inmediata: usarlas.
- En el reto de escritorio (2026-11-20) aprende mejor con un ejemplo resuelto primero y luego un ejercicio
  equivalente que hace solo. Los desensamblados reales (`objdump`) le aclararon que las etiquetas son números.

## Registro de sesiones

Ver `sesiones/` (una nota por sesión, escrita por el Escriba). Antes de 2026-11-07 el registro vivía en
documentos sueltos: ver `reportes/` y `notas/`.
