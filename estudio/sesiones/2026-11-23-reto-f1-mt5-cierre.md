# Sesión 2026-11-23 · Reto de cierre de Fase 1: mini-tarea 5 y cierre de la fase

- **Fase:** 1 — La máquina desnuda (se cierra en esta sesión).
- **Tutor:** Tutor (reto de cierre de escritorio, WSL).

## Resumen

| Mini-tarea | Resultado |
|---|---|
| 5 · Bucle con indirección | **Cumplida.** `retos/fase-1/mt5.asm` escrito solo; predicción verificada (código 18). |
| Cierre de Fase 1 | **Aprobado por el estudiante.** Reporte con Apéndice B y plan de Fase 2. |

El detalle completo (ejemplos del Tutor y respuestas finales de las cinco mini-tareas) quedó en
`reportes/fase-1-cierre.md`, Apéndice B.

---

## 1. Concepto: piezas con dirección propia

- `section .data` con `piezas: db 5, 3, 8, 2`. `mov rsi, piezas` pone en la mesa el **número del estante**;
  `mov al, [rsi]` trae la pieza; `inc rsi` avanza un estante.
- Conexión: sucesión a: {0,1,2,3} → bytes; `rsi` recorre el dominio y `[rsi]` evalúa la función.

## 2. Ejercicios de lectura

1. `mov rsi, piezas` / `inc rsi` / `inc rsi` / `mov al, [rsi]`.
   - 1.er intento: `al = 5` (ignoró los `inc`).
   - 2.º intento: un estante atrás (`piezas + 0` dos veces, `al = 3`).
   - Corregido por el Tutor: `rsi = piezas + 2`, `al = 8`.
2. `mov rsi, piezas` / `add rsi, 3` / `mov al, [rsi]` / `dec rsi` / `mov al, [rsi]`.
   - 1.er intento: sumó 3 a la **pieza** (5 + 3 = 8), confundiendo estante y pieza.
   - Con la tabla de estantes reales (`0x402000` → 5, …), lo resolvió **solo y correcto**:
     `rsi = piezas + 3`, `al = 2`, `rsi = piezas + 2`, `al = 8`.

## 3. Mini-tarea 5

- Enunciado: sumar las 4 piezas y devolver la suma como código de salida, con `rsi` (dedo), `rcx = 4`
  (contador), `rdi` (acumulador) y `add dil, [rsi]`. Por qué `dil`: `add rdi, [rsi]` leería 8 estantes.
- Pidió un ejemplo previo. El Tutor dio un bucle **sin** indirección (3 + 2 + 1 = 6 con `add dil, cl`) y le
  dejó decidir dónde van `section .data`, `[rsi]` y el avance de `rsi`.
- **Escribió `mt5.asm` solo y correcto.** Predicción: 4 vueltas (5, 3, 8, 2), `rcx = 0`, `rsi = piezas + 4`,
  código 18. La escribió **antes** de correr.
- Verificado por él en WSL: `codigo: 18`; `trazar.sh --mem piezas` coincide con la predicción.
- Pregunta: ¿ZF tras `dec rcx` en la 4.ª vuelta? Respondió **ZF = 1** ✅ («sí son iguales»). Matiz del
  Tutor: ZF = 1 significa «la última cuenta dio 0», no «son iguales»; por eso `cmp rcx, 0` sobra.
- Observaciones de la salida: `rsi` en decimal (`4202497` = `0x402001`); `[piezas] = 0x2c02080305` se lee
  de derecha a izquierda y el `2c` es el estante vecino: la máquina no sabe dónde termina el arreglo.

## 4. Cierre de la Fase 1

- El Tutor propuso el cierre con evidencia (criterio teórico 2026-10-04; mini-tareas 1–5 cumplidas).
- El estudiante pidió registrar todas las mini-tareas con los ejemplos del Tutor y sus respuestas finales.
  Las 1–4 ya estaban en las bitácoras del 2026-11-20 y 2026-11-22; ahora las cinco están en el
  **Apéndice B** de `reportes/fase-1-cierre.md`.
- Redactado `fases/fase-2.md` (C: siete temas, de C a Assembly hasta el primer buffer overflow).
- **El estudiante aprobó el reporte y el plan de Fase 2 (2026-11-23).** Fase 1 cerrada; Fase 2 en curso.

## 5. Fuera del temario

- Preguntó si el sitio es un conjunto de HTML o algo en Google Cloud. Respuesta: ambas cosas (lecciones en
  `temas/`, servidor FastAPI pensado para Cloud Run + Firestore; hoy solo corre en local).
- No le abría `localhost:8090`: el servidor no estaba levantado. Se levantó y respondió.
- Pidió subir el repo a GitHub como `chomsky-godel` (paso 3 del plan del sitio).

## Dudas abiertas y gaps detectados

- **Estante vs. pieza (dirección vs. contenido):** tropezó dos veces (ignorar los `inc`, sumar a la
  pieza). Lo resolvió con direcciones concretas en hexadecimal. Vigilar en punteros (Fase 2, tema 3).
- **ZF:** la lee como «son iguales» aun tras `dec`; matizado («la última cuenta dio 0»).
- **Escribir sin modelo:** avance claro. Con un ejemplo que no contenía la parte nueva, integró solo bucle e
  indirección.
- **Disciplina de predicción:** cumplida en esta sesión.

## Extensiones a la metáfora del taller

- **Estantes de piezas:** `section .data`; la nota al margen (`piezas:`) es el número del primer estante.
- **Mover el dedo de lectura:** `inc rsi` / `add rsi` cambian el número de estante sin tocar ninguna
  pieza; solo `[rsi]` cruza a la pieza.
- **El estante vecino no es tuyo:** la máquina no sabe dónde termina un arreglo (`2c` tras las 4 piezas).
