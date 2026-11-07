Síntesis — Fase 0, Cápsulas 1 y 2

1. Álgebra booleana

El universo de un computador es {0,1}. Sobre él se definen tres operaciones primitivas: AND, OR, NOT. La estructura resultante es un álgebra de Boole — el caso mínimo del mismo objeto que conoces en 𝒫(X) con ∪, ∩ y complemento. Las leyes son las mismas: distributividad mutua (no como en ℝ), idempotencia, De Morgan. La implicación y el XOR no son primitivos — se derivan algebraicamente, y sus igualdades se prueban sin tablas, solo con axiomas.

2. Completitud funcional

No todas las operaciones generan la lógica completa. El obstáculo es la monotonía: las funciones monótonas son cerradas bajo composición, y NOT no es monótona, así que ningún conjunto puramente monótono la alcanza. NAND y NOR rompen la monotonía — por eso cada una sola es suficiente para generar {NOT, AND, OR} y con ello toda función booleana posible. Demostraste esto explícitamente: NOT, AND y NOR expresados únicamente en términos de NAND.

3. Compuertas como materialización

El álgebra booleana deja de ser abstracta cuando un voltaje alto representa 1 y un voltaje bajo representa 0. Cada operación booleana tiene un circuito físico correspondiente — una compuerta. La completitud funcional se vuelve entonces un hecho de ingeniería: cualquier cómputo imaginable se puede construir con suficientes compuertas NAND. Los procesadores reales están hechos exactamente así.

$ La pregunta sería:

Tienes {0,1}, tienes operadores: and, or, not, nand, nor, xor, etc.LA composición de ciertos operadores diferentes nos da la misma función, la misma tabla de verdad

Todos los operadores son funciones del {0,1} en sí mismo, o del {0,1} cuadrado en el {0,1}¿Demostramos que únicamente con nand() o nor() pueden generarse todas las formulas bien formadas posibles? ¿A esto te refieres a “todo cálculo computacional puede construirse con suficientes puertas nand?”¿A qué te refieres con la lógica completa?

¿Turing probó todo esto, cierto? ¿Hasta aquí?

---
La intuición correcta, y la respuesta es exactamente tu demostración:

NOT(x) = NAND(x,x) = ¬(x·x) = ¬x

El paso clave es idempotencia: x·x = x. Ya la tenías interiorizada.

Por qué NAND sola basta — la respuesta estructural

Ya demostraste que NAND genera NOT. Ahora observa:

AND(x,y) = NOT(NAND(x,y))

Y como ya tienes NOT en términos de NAND:

AND(x,y) = NAND(NAND(x,y), NAND(x,y))

Y OR sale de De Morgan:

OR(x,y) = NOT(NOT(x) · NOT(y)) = NAND(NAND(x,x), NAND(y,y))

Es decir: NAND genera NOT, NOT+NAND genera AND, y De Morgan regala OR. Como {NOT, AND, OR} es base completa, NAND hereda esa completitud.

La razón profunda: NAND es la única operación binaria que es no monótona y no constante. Esas dos propiedades juntas son suficientes para generar toda la lógica. NOR también las cumple — por eso NOR también es funcionalmente completa sola.

Microtarea

Expresa AND(x,y) usando únicamente NAND — ya tienes la respuesta arriba, pero escríbela tú explícitamente y verifica con una tabla de verdad para (1,1) y (1,0).

---
Verificaciones perfectas. Respondo todo:

NOR = NOT OR. Es decir: NOR(x,y) = ¬(x+y). Solo es 1 cuando ambas entradas son 0.

No monótona y no constante

Constante significa que la salida no depende de las entradas — siempre 0 o siempre 1. NAND no es constante, obvio.

Monótona significa: si cambias una entrada de 0→1, la salida nunca baja de 1→0. AND y OR son monótonas — agregar un 1 nunca destruye un 1 en OR. Pero NOT viola eso: 0→1 en la entrada produce 1→0 en la salida. NAND también lo viola: NAND(1,1)=0 pero NAND(0,1)=1.

La monotonía es el obstáculo: ningún conjunto de operaciones puramente monótonas puede generar NOT — y sin NOT no puedes completar la lógica. NAND rompe la monotonía, por eso escapa esa trampa.

Conjuntos funcionalmente completos

Los principales:

- {AND, OR, NOT} — la base clásica
- {NAND} — mínimo
- {NOR} — mínimo
- {AND, NOT} — OR sale de De Morgan
- {OR, NOT} — AND sale de De Morgan
- {XOR, AND} — menos obvio, pero completo

No cualquier combinación funciona. AND+OR sin NOT no es completo — son monótonas juntas y no pueden generar NOT.

Microtarea

Expresa NOR(x,y) usando únicamente NAND. Es un buen ejercicio de composición — ya tienes todas las piezas.
