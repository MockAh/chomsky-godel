# Pendientes de contenido para el sitio

> El Escriba anota aquí, al cierre de sesión, cuando un concepto consolidado debería reflejarse en una
> lección del sitio (`temas/…`). Cada entrada: fecha, tema del sitio, qué cambiar y por qué. Se atienden
> en una rama aparte y entran con aprobación del estudiante.

## 2026-11-22 · Mapa de la CPU (`temas/cpu/mapa.html`): la libreta tiene varias marcas

- **Qué cambiar:** que la libreta (`rflags`) muestre más marcas que ZF (al menos SF y CF) y quién escribe en
  ella: las cuentas de la ALU (`sub`, `cmp`) sí; `mov` y los saltos (`je`) no, solo la leen. Opcional:
  mostrarla como gdb, con la lista de marcas encendidas (`[ PF ZF IF ]`).
- **Por qué:** en la sesión `sesiones/2026-11-22-reto-f1-mt3-mt4.md` el estudiante creía que solo `cmp`
  dejaba marcas y no sabía leer los corchetes de `$eflags`; quedó consolidado al verlo en gdb. La lección no
  menciona las marcas.
