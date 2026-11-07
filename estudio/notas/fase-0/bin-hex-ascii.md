Cápsula 6 — Representación de información: ASCII y Unicode

Hasta ahora todo han sido números. Pero cuando escribes "hola" en una computadora, eso también es una cadena de bits. ¿Cómo?

Por convención arbitraria. ASCII asigna un número de 7 bits a cada carácter del inglés: A=65, B=66, a=97, espacio=32. La letra 'A' no es 65 — se codifica como 65. Es una tabla de búsqueda, no una ley matemática.

Unicode extiende esto a todos los sistemas de escritura humanos. Un "code point" como U+00F1 (ñ) es simplemente un número natural con una interpretación asignada.

\\Cápsula 7 — Bits, bytes y palabras

Un bit es la unidad mínima: un elemento de {0,1}. Un byte es una cadena de 8 bits — por convención histórica, no por necesidad matemática.

1234 1234

1234 5678

| xxxx xxxx |

| 0101 1110 |

_ 1 byte _

Un byte tiene 2⁸ = 256 estados posibles.

Una palabra (word) es el ancho natural con el que opera el procesador. En máquinas modernas: 64 bits = 8 bytes.

xxxx xxxx | xxxx xxxx | xxxx xxxx | xxxx xxxx | xxxx xxxx | xxxx xxxx | xxxx xxxx | xxxx xxxx

_ 8 bytes_

8 x 8 = 64 bits

Esto determina cuánta memoria puede direccionar la CPU directamente: 2⁶⁴ direcciones posibles.

La jerarquía: bit → byte → palabra no es algebraica — es una convención de empaquetamiento. Pero tiene consecuencias reales: el rango de complemento a dos en 64 bits es −2⁶³ a 2⁶³−1.\\

Cápsula 6b — ASCII, Unicode y la diferencia entre código y codificación

ASCII usa 7 bits: 128 caracteres. Cubre el inglés, dígitos, puntuación y caracteres de control (como "nueva línea" o "fin de transmisión"). Nada más. No tiene ñ, no tiene 漢字, no tiene emoji.

Unicode es el proyecto de asignar un número natural único a cada símbolo de cada sistema de escritura humano — más de 150,000 hasta ahora. Cada asignación se llama code point y se nota U+XXXX. Por ejemplo: ñ = U+00F1, π = U+03C0, 🔥 = U+1F525.

Hasta aquí sí: cada símbolo → un número natural. Es una función inyectiva del conjunto de símbolos a ℕ.

Pero aquí viene la sutileza

El code point es el qué — qué número le toca a cada símbolo. La codificación es el cómo — cómo se almacena ese número en bytes. Y no hay una sola forma:

- UTF-32: cada code point ocupa exactamente 4 bytes. Simple pero desperdicia espacio — 'A' gasta 32 bits cuando le bastan 7.
- UTF-16: 2 o 4 bytes según el code point.
- UTF-8: entre 1 y 4 bytes. Los caracteres ASCII ocupan 1 byte (compatibilidad directa), los demás ocupan más.

Es decir: Unicode separa la tabla de asignación (abstracta) de la representación en memoria (concreta). Son dos funciones distintas compuestas: símbolo → code point → secuencia de bytes.

---
- Osea, me queda claro que mapeas: el símbolo en un 'natural' específico (o, code point), y luego, cada 'natural', en una secuencia de bytes;
- Lo que no entiendo es por qué: el rango de complemento a dos en 64 bits es −2⁶³ a 2⁶³−1; ¿No debería ser -2^(31) a 2^(31) - 1?

- Claro, osea, únicamente requieres el último bit, de los 8, para girar las cosas;
- 1000 0000 es tal que su complemento a dos es 0111 1111 + 1 = 1000 0000
- Ese ´último slot' funciona como la bisagra que te da todo el espectro entre −2⁷ a 2⁷−1
- Y es como dices: es 1 bit de signo + 7 bits de magnitud.
- Claro, ya: Son 1+todos y luego 0+todos ( en el entendido de, como dices, si empieza con 1 es positivo y si empieza con 0 es negativo); por eso no divides el 64 en dos, o el 8 en dos, sino es el 63 íntegro y el 7 íntegro, i.e. −2⁷ a 2⁷−1

---
1. Tu reconstrucción es correcta, con un matiz: la dirección almacenada en memoria ocupa 8 bytes, pero apunta a una celda de 1 byte. La asimetría es real e intencional.

2. ¿La palabra varía de 1 a 8 bytes?

La palabra arquitectónica es fija — 8 bytes en un procesador de 64 bits. Pero la CPU tiene instrucciones que operan sobre fragmentos menores: cargar 1 byte, 2 bytes, 4 bytes, o los 8 completos. No cambia el tamaño de la palabra; cambia qué porción se manipula.

Además existen instrucciones SIMD que operan sobre 128, 256, incluso 512 bits a la vez — más grandes que una palabra. La palabra es el ancho "natural" pero no el único en el que la CPU puede trabajar.

---
Buena pregunta — hay dos dimensiones distintas y vale la pena separarlas.

Dimensión 1: tamaño de los operandos

Un procesador de 64 bits puede operar nativamente con operandos de hasta 64 bits por operando. Si quieres sumar dos números de 128 bits, eso requiere varias instrucciones — se rompe la atomicidad.

Dimensión 2: cantidad de operandos

Las instrucciones aritméticas de la CPU son binarias: reciben dos operandos a la vez. No hay una instrucción "suma estos tres números" en x86 o ARM estándar.

Entonces sumar 3 palabras de 8 bytes no es atómico — aunque cada operando quepa en un registro de 64 bits. La CPU lo ejecuta así:

instrucción 1: ADD A, B → resultado parcial instrucción 2: ADD resultado_parcial, C → resultado final

Son dos pasos, no uno. La atomicidad se rompe por aridad, no por tamaño.

Por qué la ALU es binaria

El hardware del sumador físico tiene exactamente dos entradas de 64 bits y una salida de 64 bits (más un carry). Para sumar 3, necesitas pasar por el sumador dos veces, almacenando el resultado intermedio. Eso son dos instrucciones por construcción.

Resumen: atómico = una sola instrucción. Eso requiere (a) operandos que quepan en el ancho de palabra, y (b) que la operación coincida con una instrucción real de la CPU — que para aritmética significa binaria.

Microtarea pendiente: 2³⁴ en base 10 aproximadamente.
