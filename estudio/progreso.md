# Progreso del estudiante

> Documento vivo. **Solo lo actualiza el Escriba**, al cierre de cada sesión, con base en lo que pasó en
> ella. No se inventa progreso: si algo no está registrado, se dice «sin registro».
> Fechas siempre absolutas (AAAA-MM-DD).

## Estado actual

- **Fase actual:** 1 — La máquina desnuda.
- **Criterio de salida de la fase:** cumplido en lo teórico (2026-10-04, trazados A.1 y A.2 del reporte de cierre).
- **Pendiente para cerrar la fase:** el **reto de cierre de escritorio** (`retos/fase-1-reto-cierre.md`):
  escribir, ensamblar y ejecutar Assembly x86-64 en WSL con nasm, ld y gdb.
  - Mini-tarea 1 (preparar el taller): sin registro de resultado.
  - Mini-tareas 2 a 5: sin empezar (sin registro).
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
- Sin otras dudas abiertas registradas.

## Observaciones de los tutores

- Responde mejor con metáforas físicas sostenidas (el grifo, el taller) que con densidad técnica sin ancla;
  ver `lenguaje-compartido.md`.
- Las correspondencias formales (MT ↔ CPU, memoria como función f: D → {0,1}⁸, F(F(x)) como indirección)
  le dan intuición inmediata: usarlas.

## Registro de sesiones

Ver `sesiones/` (una nota por sesión, escrita por el Escriba). Antes de 2026-11-07 el registro vivía en
documentos sueltos: ver `reportes/` y `notas/`.
