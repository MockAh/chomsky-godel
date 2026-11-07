2³⁴ ≈ 10¹⁰ — correcto. Más precisamente: 2³⁴ = 2³⁰ · 2⁴ ≈ 10⁹ · 16 ≈ 1.6 × 10¹⁰. Es decir, ~16 mil millones de GB = ~16 exabytes de espacio direccionable. Cantidad absurdamente grande para cualquier RAM real, lo cual es el punto.

## Síntesis — Fase 0, parte II

Representación posicional

Toda base b representa números como sumas de la forma dₖ·bᵏ + ... + d₁·b¹ + d₀·b⁰. La estructura es la misma; cambia el alfabeto y la base. Binario usa {0,1}, octal {0..7}, decimal {0..9}, hex {0..9, A..F}.

El hecho clave que descubrimos: cuando una base es potencia exacta de otra (b₁ = b₂^k), la conversión entre ellas es concatenación pura, sin aritmética. Hex ↔ binario funciona porque 16 = 2⁴ (4 bits por dígito hex). Octal ↔ binario funciona porque 8 = 2³ (3 bits por dígito octal). La razón profunda: los pesos posicionales se alinean — al multiplicar un dígito hex por 16ᵏ, sus 4 bits ocupan la franja 2^(4k) a 2^(4k+3) sin traslapar la franja del siguiente dígito.

Por eso hex es el lenguaje natural para hablar de bits: es solo binario reagrupado en bloques de 4, más cómodo de leer.

Aritmética binaria y complemento a dos

La suma binaria funciona igual que la decimal — con carry cuando se supera el dígito máximo. Una compuerta XOR da el bit de suma y una AND da el carry: eso es un half adder, el bloque básico de la ALU.

La resta se evita: las computadoras solo tienen circuitos sumadores. Para calcular A − B, computan A + (−B), donde −B se obtiene por complemento a dos: invertir todos los bits de B y sumar 1. Es un homomorfismo entre la negación en ℤ y una operación bit a bit, lo que permite que toda la aritmética con signo se reduzca a sumas.

En n bits, el rango representable es −2^(n−1) a 2^(n−1) − 1. El bit más significativo es el signo: 0 → positivo, 1 → negativo. Solo se gasta un bit en el signo, no la mitad — los demás n−1 son magnitud íntegra.

Asimetría notable: hay un negativo más que positivos, porque el cero ocupa lugar en el lado positivo y no existe "−0". Consecuencia: el menor negativo (ej. −128 en 8 bits) es su propio complemento a dos. La función "negar" tiene un punto fijo no trivial — rompe la involución y la estructura de grupo.

ASCII, Unicode, codificaciones

Texto y números no son cosas distintas en una computadora — los caracteres se codifican como números por convención.

ASCII usa 7 bits para 128 caracteres. Cubre inglés básico, dígitos, puntuación y controles. Limitado.

Unicode es el proyecto de asignar un número natural único (un code point) a cada símbolo de todo sistema de escritura humano: ñ = U+00F1, π = U+03C0, 🔥 = U+1F525. Más de 150,000 símbolos catalogados. Es una función inyectiva del conjunto de símbolos a ℕ.

Distinción clave: el code point es abstracto; la codificación es concreta. Hay dos funciones compuestas: símbolo → code point → secuencia de bytes. Las codificaciones más comunes:

- UTF-32: 4 bytes por code point, fijo. Simple, derrochador.
- UTF-16: 2 o 4 bytes según el code point.
- UTF-8: 1 a 4 bytes. Los caracteres ASCII gastan exactamente 1 byte — compatibilidad histórica con texto plano antiguo.

UTF-8 dominó la web porque el texto típico (HTML, código, JSON) es mayoritariamente ASCII, donde es 4× más compacto que UTF-32.

Bits, bytes, palabras y direccionamiento

Jerarquía: bit (mínimo) → byte (8 bits, convención) → palabra (ancho nativo del procesador).

La palabra es el tamaño de los registros internos de la CPU y de los punteros. Un procesador de 64 bits tiene palabras de 64 bits = 8 bytes. Eso determina cuántas direcciones de memoria puede manejar nativamente: 2⁶⁴ ≈ 1.6 × 10¹⁹.

La memoria es direccionable por byte: cada dirección apunta a una celda de 1 byte, aunque la dirección misma sea de 8 bytes. La asimetría (puntero grande, celda chica) es intencional: permite granularidad fina para datos de cualquier tamaño sin desperdiciar capacidad real de RAM.

Atomicidad — concepto clave

Una operación es atómica si la CPU la ejecuta en una sola instrucción. Eso requiere dos cosas independientes:

- Operandos dentro del ancho de palabra: sumar dos números de 128 bits en un procesador de 64 bits requiere varias instrucciones.
- Aridad compatible con la instrucción: las operaciones aritméticas de la CPU son binarias — toman exactamente dos operandos. Sumar tres números no es atómico aunque cada uno quepa en un registro: el hardware del sumador tiene físicamente dos entradas y una salida.

La ALU es binaria por construcción. Operaciones más amplias (SIMD: 128, 256, 512 bits) o más estrechas (sub-word: cargar 1 byte, 2 bytes) existen como instrucciones específicas, pero la palabra sigue siendo el ancho de referencia.

Hilo conductor de toda la fase hasta aquí

Empezamos con álgebra abstracta sobre {0,1}. Vimos que esa álgebra se materializa físicamente en compuertas, que NAND sola basta para generar toda función booleana, y que esas funciones implementan tanto aritmética (sumadores, restadores via complemento) como representación de información (números en cualquier base, texto via convenciones). Finalmente, esas operaciones se organizan en registros del ancho de palabra, y la memoria se direcciona por bytes con punteros de palabra. Todo el aparato está sostenido por una sola operación lógica primitiva — NAND — repetida miles de millones de veces en silicio.
