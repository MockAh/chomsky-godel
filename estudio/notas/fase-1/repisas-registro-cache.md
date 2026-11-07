Tienes razón — usé "register allocation" sin definirlo. Lo retiro por ahora; lo retomamos cuando toque. Vamos limpio.

1.2 — ¿1 GP = 1 palabra = ancho de la variable?

Casi. Afino una pieza para que no se cuele un error:

- 1 GP = 1 palabra → correcto y fijo. El registro mide exactamente una palabra (8 bytes en 64 bits). Es físico, no cambia.
- = ancho de la variable → no siempre. La variable cabe en la palabra, pero puede ser más chica. Un carácter ocupa 1 byte; va en un registro de 8 bytes y deja 7 vacíos. Lo que es fijo es el recipiente (el registro = 1 palabra). Lo que varía es cuánto del recipiente usa el dato.

Resumen: el registro tiene tamaño fijo (1 palabra); la variable tiene tamaño propio, igual o menor. Si fuera mayor que la palabra, no cabe en un solo registro — se parte.

1.3 — Diferencia entre registro y memoria

Sigamos la casa.

Registro = la mesa de trabajo. Solo caben ~16 objetos. Es donde efectivamente trabajas: la ALU solo toca lo que está en la mesa. Diminuta, pero tienes todo al alcance instantáneo de la mano.

Memoria (RAM) = los estantes y armarios de la casa. Cabe casi todo (miles de millones de objetos). Pero la ALU no alcanza los estantes: no puede operar sobre algo guardado. Tienes que traerlo a la mesa primero, trabajarlo, y devolverlo al estante.

Tres diferencias concretas:

|  | Registro (mesa) | Memoria (estantes) |
|---|---|---|
| Cantidad | ~16, fija | miles de millones |
| Acceso | la ALU opera directo | hay que traer/llevar primero |
| Identificación | por nombre (rax, rbx) | por dirección (un número) |

Esa última fila es clave y la marco: a un registro lo llamas por nombre propio — hay 16, cada uno tiene el suyo. A una celda de memoria la llamas por dirección — un número, porque son demasiadas para tener nombres. (Esto enlaza directo con el direccionamiento por byte de Fase 0.)

Microtarea. Tienes dos variables, a y b, guardadas en estantes (memoria), y quieres a + b. Ordena estos pasos — y dime cuál de ellos no puede saltarse:

- Sumar en la ALU
- Traer b a la mesa
- Traer a a la mesa
- Devolver el resultado a un estante

---
Orden perfecto. Y la pregunta correcta es la que tú hiciste — cuál puedes saltarte. La respuesta es el paso 4.

Por qué. Después de sumar (paso 3), el resultado ya está en la mesa, en un registro. Existe, está listo, lo tienes en la mano. Devolverlo al estante (paso 4) solo sirve si:

- vas a necesitar la mesa para otra cosa y no quieres que se pierda, o
- ese resultado tiene que persistir más allá del trabajo inmediato.

Si lo siguiente que vas a hacer es, digamos, multiplicar ese resultado por otra cosa, lo dejas en la mesa y sigues. Guardarlo y volver a traerlo sería trabajo desperdiciado.

Los pasos 1, 2, 3 sí son obligatorios bajo nuestra regla: la ALU solo toca la mesa, así que ambos operandos tienen que subir, y la suma es el cómputo mismo. Pero el paso 4 es una decisión, no una necesidad.

Y aquí está el punto que llevo dos cápsulas rondando. ¿Por qué te molestarías en devolver algo al estante si la mesa es tan cómoda? Porque la mesa solo tiene 16 lugares. La finitud que vimos en los registros te obliga a estar decidiendo constantemente qué mantener a mano y qué guardar.

Esa tensión —mesa diminuta y rapidísima contra estantes enormes y lejanos— es el motivo de que cargar de memoria no cueste lo mismo que operar en un registro. Hay una distancia real, medible en tiempo, entre la mesa y los estantes.

Pregunta, sin tecnicismos todavía: si tuvieras una mesa de trabajo minúscula pero los estantes estuvieran muy lejos —digamos, en otra habitación— ¿qué tipo de truco se te ocurriría para no estar yendo y viniendo a la otra habitación todo el tiempo? Piensa como organizarías el espacio, no como ingeniero.

---
Las dos ideas son reales y existen en hardware. Y lo mejor: tú mismo detectaste el límite de cada una. Vamos a verlas y luego te muestro la pieza que falta.

Idea 1 — un cargador dedicado. Sí existe: separar a quien opera de quien acarrea. Pero fíjate qué resuelve y qué no — no acorta la distancia, solo hace que el operador no se quede esperando de brazos cruzados mientras el otro va y viene. Esconde la espera, no la elimina. Útil, pero parcial.

Idea 2 — una sola habitación. Choca con la física, y lo viste: una mesa al alcance de la mano tiene que ser chica (si no, ya no alcanzas todo). Y los estantes que guardan miles de millones de cosas ocupan espacio — no caben pegados a la mesa. Pequeño-y-cercano y grande-y-lejano están en tensión irreducible. No puedes tener una sola habitación que sea ambas.

La pieza que falta: no elijas — apila niveles.

En vez de una mesa y un almacén lejano, pones escalas intermedias:

- Mesa (registros): ~16 cosas, al instante.
- Repisita pegada a la mesa: unas pocas decenas de cosas, casi instantánea. Guardas aquí copias de lo que acabas de usar.
- Estantería de la habitación: más cosas, un poco más lejos.
- Almacén (RAM): todo, pero lejos.

Esto es la caché: pequeñas memorias intermedias que guardan copias de lo que usaste recientemente, cada una más grande y más lenta conforme se aleja de la mesa. (Es la "jerarquía de caché" que apareció de pasada en Fase 0; ahora le damos cuerpo.)

La apuesta detrás de todo el diseño: lo que usaste hace un momento, probablemente lo vuelvas a usar pronto. Así que en vez de devolverlo al almacén lejano, dejas una copia en la repisita.

Pregunta. Esa apuesta —"lo reciente se repite"— ¿la dirías razonable o arriesgada? Piensa en un programa cualquiera: ¿qué hacen los programas todo el tiempo que justamente repite acceder a los mismos pocos datos una y otra vez?
