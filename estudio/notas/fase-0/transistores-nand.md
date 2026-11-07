Hecho — más metáforas, menos densidad técnica. La precisión sigue ahí, pero entra por la puerta principal.

Cápsula 8 — Del transistor a la compuerta

Hasta ahora todo ha sido álgebra. Pero la pregunta que cierra la Fase 0 es física: ¿cómo se hace que un trozo de silicio piense?

La metáfora del grifo

Imagina un grifo de agua, pero modificado. En lugar de una manija que abres con la mano, este grifo se abre cuando otro grifo le manda agua a su control. Si llega agua al control, el grifo principal se abre y deja pasar el flujo. Si no llega, queda cerrado.

Eso es un transistor: un interruptor que no se opera con los dedos, sino con otra señal eléctrica.

Tres terminales:

- Uno donde entra la "señal de mando" (la corriente que lo abre o cierra)
- Dos por donde fluye la corriente principal cuando está abierto

Cuando llega voltaje al terminal de mando → el transistor conduce. Cuando no llega → el transistor bloquea. Exactamente como un grifo controlado a distancia.

De grifos a lógica

Conecta dos transistores en serie — uno detrás de otro como dos grifos en la misma tubería. Para que el agua llegue al final, ambos tienen que estar abiertos. Si solo uno está cerrado, no pasa nada.

Eso es una compuerta AND.

Conéctalos en paralelo — dos tuberías que desembocan en una. Para que llegue agua al final, basta con que al menos uno esté abierto.

Eso es una compuerta OR.

Y un solo transistor configurado para invertir su estado (cuando recibe señal, bloquea; cuando no recibe, conduce) es una compuerta NOT.

Toda la lógica que estudiaste — todo el álgebra de Boole, todo el aparato del que NAND es suficiente — termina siendo grifos diminutos conectados de maneras específicas.

El milagro de escala

Un procesador moderno tiene del orden de decenas de miles de millones de transistores en un chip del tamaño de una uña. Cada uno es un grifo microscópico que se abre y cierra miles de millones de veces por segundo. Toda la abstracción matemática que hemos construido — desde {0,1} hasta la representación de Unicode — está físicamente sostenida por ese enjambre de interruptores.

Es la respuesta a la pregunta de cómo una computadora "piensa": no piensa. Tiene billones de grifos diminutos abriéndose y cerrándose en patrones tan complejos que parecen pensamiento.

Microtarea (sin código, solo razonamiento)

Si una compuerta AND se hace con dos transistores en serie, y una compuerta NOT con uno solo configurado al revés, ¿cuántos transistores mínimo necesitarías para construir una compuerta NAND? Recuerda que NAND = NOT(AND).

---
El número es correcto — 3 transistores — pero la posición está al revés. Vamos con la metáfora.

Por qué el NOT va al final, no al principio

Si pones el NOT al comienzo de la cadena, lo que estás invirtiendo es una sola entrada, no el resultado completo. Sería como decir: "el primer grifo se abre cuando no le mandan agua". El resultado es ¬A · B — una función completamente distinta.

NAND significa "el AND completo, negado". Primero dejas que la cadena haga su trabajo (computar A · B), y después inviertes lo que sale.

La construcción correcta:

Dos grifos en serie computan A · B en su salida → un tercer grifo configurado como NOT toma esa salida y la invierte → NAND

El NOT está al final, operando sobre el resultado del AND, no sobre una entrada del AND.

Un detalle elegante que vale la pena conocer

En la implementación real con tecnología CMOS (la que usan los chips modernos), NAND se construye con solo 4 transistores en una configuración directa, sin necesidad de "hacer un AND y luego negarlo". Resulta que NAND es físicamente más simple que AND.

De hecho, AND en CMOS se construye como NAND seguido de NOT — el orden es inverso al pedagógico. Eso explica parte del prestigio de NAND: no solo es funcionalmente completa, sino que también es la compuerta más barata de fabricar.

La naturaleza eligió NAND, no AND, como su pieza favorita.

Microtarea

Sigue el patrón: si NAND es "AND negado al final" usando 3 transistores, ¿cómo construirías una compuerta NOR con la misma lógica metafórica? ¿Cuántos transistores y en qué configuración?

---
Primera respuesta — 3 transistores

Sí, perfecto. Dos grifos en paralelo computan A + B en su salida común, y un tercer grifo configurado como NOT invierte ese resultado. Es el espejo exacto de la construcción de NAND: cambia "serie" por "paralelo", y obtienes el dual.

NAND y NOR son duales en este sentido — uno se obtiene del otro intercambiando AND por OR. La simetría de De Morgan está cableada literalmente en el hardware: serie ↔ paralelo es la versión física de AND ↔ OR.

Segunda respuesta — 4 transistores vía De Morgan

También es correcta. Aplicaste ¬(x+y) = ¬x · ¬y y construiste cada NOT por separado, luego los conectaste en serie para el AND. Te queda:

- NOT en x → 1 transistor
- NOT en y → 1 transistor
- AND de los dos resultados → 2 transistores en serie
- Total: 4 transistores

Funciona y produce la misma función — pero gasta un transistor de más comparado con la primera ruta.

El punto pedagógico

Acabas de descubrir algo que los diseñadores de chips conocen bien: diferentes expresiones algebraicamente equivalentes consumen diferentes cantidades de hardware. La función es la misma, pero el costo físico no.

Por eso existe toda una disciplina — la minimización lógica — dedicada a encontrar la expresión booleana más barata para una función dada. El álgebra de Boole no solo describe qué se puede computar: también dicta cuánto silicio cuesta computarlo.
