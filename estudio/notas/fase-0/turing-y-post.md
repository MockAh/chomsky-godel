Los operadores como funciones

Exacto. Son funciones de la forma f: {0,1}ⁿ → {0,1}. NOT es n=1, los demás son n=2. El conjunto de todas las funciones posibles de ese tipo es finito y contable — para n=2 hay exactamente 2^(2²) = 16 funciones booleanas distintas. La completitud funcional dice que NAND genera todas ellas por composición.

"Lógica completa" y fórmulas bien formadas

Sí, es exactamente lo que dices: toda función booleana {0,1}ⁿ → {0,1} es expresable como composición de NANDs. Y como cualquier cómputo real se reduce a evaluar funciones booleanas sobre bits, NAND basta para todo cómputo posible a nivel de circuito.

¿Turing probó esto?

No. Esto lo demostró Emil Post en 1941 — caracterizó completamente qué conjuntos de operadores son funcionalmente completos. Se llama el Teorema de Post.

Turing demostró algo distinto y de otra capa: que existe una máquina abstracta capaz de simular cualquier cómputo computable — la Máquina de Turing. Son resultados complementarios: Post habla de qué operaciones bastan a nivel lógico, Turing habla de qué procedimientos son computables en absoluto.

Los dos juntos delimitan qué puede y qué no puede computarse — pero son teoremas diferentes, de autores diferentes.

---
Hay un error de notación pequeño pero importante, y luego la respuesta al fondo.

Corrección

Para n variables, el dominio es {0,1}ⁿ, que tiene 2ⁿ elementos. Una función booleana asigna 0 o 1 a cada elemento del dominio, entonces hay:

2^(2^n) funciones distintas — no n^(2²)

Verifica: n=2 → 2^(2²) = 2^4 = 16. ✓

La exponenciación es 2^(2^n), y crece muy rápido: n=3 da 256, n=4 da 65536.

El conjunto total

Sí — tomando la unión sobre todos los n∈ℕ obtienes una colección infinita de funciones booleanas. Y esa unión es numerable: unión numerable de conjuntos finitos es numerable.

¿Se usa Choice?

¿NAND genera ese conjunto infinito?

Sí, pero con precisión: NAND con n variables de entrada, compuesta consigo misma de todas las formas posibles, genera cualquier función booleana de cualquier aridad finita. El mecanismo es composición — puedes construir circuitos con tantas entradas como necesites encadenando compuertas NAND de 2 entradas.

Lo que esto significa computacionalmente

Todo dato en una computadora es una cadena finita de bits — un elemento de {0,1}ⁿ para algún n finito. Todo cómputo es una función {0,1}ⁿ → {0,1}ᵐ, descomponible en funciones booleanas. NAND genera todas ellas. Por eso los procesadores reales están construidos con millones de compuertas NAND.

- Entiendo entonces que lo que harías sería descomponer todas las combinaciones posibles de nands en clases de equivalencia; Así tienes todas las que son realmente distintas. Es en realidad este conjunto el que tiene 2^2^n. ¿Correcto?
