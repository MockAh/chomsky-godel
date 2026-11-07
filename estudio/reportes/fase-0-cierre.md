**FASE 0 — REPORTE DE CIERRE**

El puente: de la matemática a la lógica de la máquina

Estudiante: Guillermo

Programa: Ingeniería en Sistemas y Ciberseguridad

## Propósito de este documento

Este reporte cierra la Fase 0 del programa. Recoge los conceptos vistos, los desarrollos relevantes y los ejercicios resueltos durante las sesiones. Está pensado como referencia consultable: si en una fase posterior surge una duda sobre representación de datos, álgebra booleana o el modelo del procesador, este documento debe bastar para refrescar la base.

La estructura sigue el orden temático en que se desarrollaron las cápsulas, no el cronológico. El apéndice final reúne los ejercicios resueltos en sesión, anotados con la lógica que los justificó.

## 1. Álgebra booleana

### 1.1 Definición operacional

Un computador opera sobre el conjunto {0,1}. Sobre ese conjunto se definen tres operaciones primitivas:

- AND (·): produce 1 únicamente cuando ambos operandos son 1.
- OR (+): produce 1 cuando al menos un operando es 1.
- NOT (¬): invierte el valor del único operando.

Cualquier cómputo realizado por un computador —desde una suma aritmética hasta la representación gráfica de una página web— es, en última instancia, composición de estas tres operaciones.

### 1.2 Conexión con la formación matemática del estudiante

Esta estructura no es una analogía: el álgebra booleana es literalmente un retículo distributivo complementado, en el sentido formal de Birkhoff. El conjunto {0,1} con AND, OR, NOT satisface todos los axiomas del álgebra de Boole:

- Idempotencia: x · x = x ; x + x = x
- Conmutatividad: x · y = y · x ; x + y = y + x
- Asociatividad.
- Distributividad mutua: x · (y + z) = x·y + x·z ; y también x + (y · z) = (x + y) · (x + z). Esta propiedad —que ambas operaciones distribuyan entre sí— no tiene análogo en ℝ.
- Existencia de complemento: para cada x existe ¬x tal que x · ¬x = 0 y x + ¬x = 1.
- Leyes de De Morgan: ¬(x · y) = ¬x + ¬y ; ¬(x + y) = ¬x · ¬y.

El ejemplo prototípico de álgebra de Boole es el conjunto potencia 𝒫(X) con unión, intersección y complemento. La estructura sobre {0,1} con AND, OR, NOT es el caso mínimo del mismo objeto matemático.

### 1.3 Operaciones derivadas

XOR e implicación material no son operaciones primitivas: se construyen como composiciones de AND, OR y NOT. Las identidades verificadas durante la sesión:

```
XOR(x, y)         = (x · ¬y) + (¬x · y)
Implicación x → y = ¬(x · ¬y) = ¬x + y
```

La equivalencia entre ¬(x · ¬y) y ¬x + y se demuestra de dos maneras: por tabla de verdad (verificando los cuatro casos posibles) o por manipulación algebraica usando De Morgan y la identidad 1 + A = 1.

## 2. Completitud funcional

### 2.1 El espacio de funciones booleanas

Para n variables de entrada, una función booleana es una función f: {0,1}ⁿ → {0,1}. El dominio tiene 2ⁿ elementos, y para cada uno se asigna 0 o 1. Por tanto el número de funciones booleanas distintas con n variables es:

```
2^(2^n)
```

Para n = 1, hay 4 funciones (identidad, negación, constante 0, constante 1). Para n = 2, hay 16. Para n = 3, hay 256. La unión sobre todos los n es un conjunto infinito numerable —unión numerable de finitos—, propiedad cuya demostración requiere alguna forma del Axioma de Elección (específicamente, Elección Numerable).

### 2.2 Conjuntos funcionalmente completos

Un conjunto de operadores es funcionalmente completo si toda función booleana de cualquier aridad finita puede expresarse como composición de operadores del conjunto. Los principales conjuntos completos:

- {AND, OR, NOT} — la base clásica.
- {NAND} — base mínima, un solo operador.
- {NOR} — también mínima.
- {AND, NOT} — OR se deriva por De Morgan.
- {OR, NOT} — AND se deriva por De Morgan.
- {XOR, AND} — completitud menos obvia, pero verificable.

No cualquier subconjunto funciona. {AND, OR} sin NOT no es completo: ambas son monótonas, y la composición de monótonas es monótona, así que NOT no puede generarse.

```
2.3 Monotonía y constancia
```

Una función booleana es constante si su salida es independiente de las entradas: f(x) = 0 para todo x, o f(x) = 1 para todo x. No hay flujo de información de entrada a salida.

Una función es monótona si su salida nunca decrece cuando una entrada cambia de 0 a 1. Formalmente: si x ≤ x' componente a componente, entonces f(x) ≤ f(x'). AND y OR son monótonas: agregar un 1 nunca destruye un 1 en OR; quitarlo nunca crea uno nuevo en AND.

NOT no es monótona: la entrada crece de 0 a 1 pero la salida decrece de 1 a 0. NAND tampoco lo es: NAND(0,1) = 1, pero NAND(1,1) = 0.

Consecuencia estructural: el conjunto de funciones monótonas es cerrado bajo composición. Cualquier base funcional que pretenda generar la lógica completa debe contener al menos un operador no monótono y no constante. El Teorema de Post (Emil Post, 1941) caracteriza completamente qué conjuntos de operadores son funcionalmente completos.

Nota histórica: este resultado se debe a Post, no a Turing. Turing demostró un teorema distinto y de otra capa de abstracción —la existencia de una máquina universal capaz de simular cualquier procedimiento computable—. Los dos resultados son complementarios pero independientes.

## 3. Compuertas lógicas

### 3.1 Materialización física del álgebra

Una compuerta lógica es la realización física de una operación booleana. Toma uno o dos voltajes como entrada y produce un voltaje como salida, bajo la convención:

- Voltaje alto (~3.3 V o ~5 V) representa el valor 1.
- Voltaje bajo (~0 V) representa el valor 0.

Cada operación booleana tiene su compuerta correspondiente. El comportamiento eléctrico de la compuerta reproduce exactamente la tabla de verdad de la operación.

### 3.2 Construcción a partir de transistores

Una compuerta lógica no es indivisible: se construye con transistores —interruptores controlados eléctricamente—. Un transistor tiene tres terminales:

- Terminal de control: recibe una señal eléctrica que abre o cierra el paso.
- Dos terminales de paso: por donde fluye la corriente principal cuando el transistor está abierto.

Cuando llega voltaje al terminal de control, el transistor conduce; cuando no, bloquea. La metáfora útil es la de un grifo de agua cuya manija se opera con otro flujo: el transistor es un interruptor accionado por otra señal eléctrica, no por una mano humana.

#### Configuraciones físicas

- Dos transistores en serie computan AND: para que la corriente fluya hasta el final, ambos deben estar abiertos.
- Dos transistores en paralelo computan OR: basta con que uno esté abierto para que la corriente llegue.
- Un transistor configurado de modo inverso computa NOT: conduce cuando no recibe señal y bloquea cuando recibe.

La correspondencia serie ↔ AND y paralelo ↔ OR es la realización física de la dualidad de De Morgan. Las leyes algebraicas se reflejan literalmente en la topología del circuito.

### 3.3 NAND como pieza fundamental

NAND es funcionalmente completa por sí sola: cualquier función booleana se puede construir con suficientes NANDs. Esto se demuestra mostrando que NAND genera {NOT, AND, OR}:

```
NOT(x)     = NAND(x, x)
AND(x, y)  = NAND(NAND(x, y), NAND(x, y))
OR(x, y)   = NAND(NAND(x, x), NAND(y, y))
```

La elegancia de NAND no es solo lógica sino también de ingeniería. En tecnología CMOS, NAND se construye con cuatro transistores en configuración directa, sin necesidad de construir un AND y luego negarlo. De hecho, AND en CMOS se implementa como NAND seguido de NOT. La operación 'natural' del hardware es NAND, no AND.

### 3.4 Escala

Un procesador moderno contiene del orden de decenas de miles de millones de transistores en un chip del tamaño de una uña. Cada uno conmuta entre conducción y bloqueo miles de millones de veces por segundo. La abstracción matemática completa —desde {0,1} hasta la representación de Unicode— está físicamente sostenida por ese enjambre de interruptores microscópicos.

## 4. Representación posicional de números

### 4.1 Estructura general

Cualquier base b ≥ 2 permite representar números naturales mediante la expansión:

```
N = dₖ·bᵏ + dₖ₋₁·bᵏ⁻¹ + ... + d₁·b¹ + d₀·b⁰
```

donde cada dᵢ es un dígito del alfabeto correspondiente: {0,1} para binario, {0..7} para octal, {0..9} para decimal, {0..9, A..F} para hexadecimal.

La estructura es la misma; cambia el alfabeto y la base. La representación posicional es, en términos estructurales, un homomorfismo entre cadenas de símbolos y números naturales.

### 4.2 Conversión entre bases potencia de 2

Cuando una base es potencia exacta de otra (b₁ = b₂^k), la conversión entre ellas es por concatenación directa, sin necesidad de operaciones aritméticas:

- Hexadecimal ↔ binario: cada dígito hex corresponde exactamente a 4 bits, porque 16 = 2⁴.
- Octal ↔ binario: cada dígito octal corresponde a 3 bits, porque 8 = 2³.

La razón estructural: los pesos posicionales se alinean. Al multiplicar un dígito hex por 16ᵏ = 2^(4k), sus 4 bits ocupan exclusivamente la franja de potencias de 2 que va de 2^(4k) a 2^(4k+3). Esa franja no se traslapa con la del dígito siguiente. La suma de las contribuciones de cada dígito es entonces, bit a bit, simplemente la concatenación.

#### Tabla de conversión hex → binario

| **Hex** | **Binario** | **Hex** | **Binario** |
|---|---|---|---|
| 0 | 0000 | 8 | 1000 |
| 1 | 0001 | 9 | 1001 |
| 2 | 0010 | A | 1010 |
| 3 | 0011 | B | 1011 |
| 4 | 0100 | C | 1100 |
| 5 | 0101 | D | 1101 |
| 6 | 0110 | E | 1110 |
| 7 | 0111 | F | 1111 |

Por la misma razón estructural, hex es la notación natural para hablar de bits en sistemas. No es realmente una base distinta del binario en la práctica; es binario reagrupado en bloques de 4.

## 5. Aritmética binaria y complemento a dos

### 5.1 Suma binaria

La suma en binario sigue el mismo algoritmo posicional que la suma decimal, con carry cuando se supera el dígito máximo (1 en lugar de 9). Las reglas básicas:

```
0 + 0 = 0
0 + 1 = 1
1 + 1 = 10  (cero con carry de 1)
1 + 1 + 1 = 11  (uno con carry de 1)
```

### 5.2 Half adder y full adder

El circuito mínimo que suma dos bits se llama half adder. Usa exactamente dos compuertas:

- Una XOR produce el bit de suma.
- Una AND produce el carry.

Para sumar palabras completas se encadenan full adders, cada uno acepta también un carry de entrada. Toda la aritmética entera del procesador se construye encadenando estos bloques.

### 5.3 Complemento a dos

Las computadoras no implementan circuitos de resta. Toda resta se reduce a una suma con el operando complementado:

```
A − B  ≡  A + (−B)
```

La representación de −B se obtiene por complemento a dos: invertir todos los bits de B y sumar 1. Algebraicamente esto define un homomorfismo entre la negación en ℤ y una operación bit a bit.

### 5.4 Rango y bit de signo

En n bits, el rango representable en complemento a dos es:

```
−2^(n−1)  ≤  x  ≤  2^(n−1) − 1
```

El bit más significativo funciona como bit de signo: 0 indica positivo, 1 indica negativo. Se gasta exactamente un bit en el signo, no la mitad de los bits. Para 8 bits: rango −128 a 127. Para 64 bits: rango −2⁶³ a 2⁶³ − 1.

### 5.5 Asimetría y punto fijo

El rango tiene un negativo más que positivos. El cero ocupa un lugar en el lado positivo (representado como 0...0) y no existe '−0' independiente. La consecuencia: el valor mínimo (en 8 bits, −128 = 1000 0000) es punto fijo de la negación —su complemento a dos es él mismo.

Verificación: complemento de 1000 0000 → invertir = 0111 1111 → sumar 1 = 1000 0000. La función 'negar' no es involutiva sobre el conjunto representable: tiene un punto fijo no trivial, lo cual rompe la estructura de grupo.

## 6. Representación de información: ASCII y Unicode

### 6.1 Códigos de carácter

Texto y números no son objetos esencialmente distintos en una computadora. Los caracteres se codifican como números naturales por convención. La asignación carácter → número es arbitraria en sentido matemático; está fijada por estándares.

### 6.2 ASCII

ASCII (American Standard Code for Information Interchange) usa 7 bits para representar 128 caracteres: alfabeto inglés en mayúsculas y minúsculas, dígitos, signos de puntuación y caracteres de control (salto de línea, retorno de carro, tabulador, fin de transmisión, etc.). Su limitación principal: no incluye caracteres acentuados, escrituras no latinas, ni símbolos modernos.

### 6.3 Unicode

Unicode es el proyecto de asignar un número natural único a cada símbolo de todo sistema de escritura humano. La asignación es una función inyectiva del conjunto de símbolos a ℕ. Cada número asignado se llama code point y se nota U+XXXX, donde XXXX es el valor en hexadecimal.

Ejemplos: A = U+0041, ñ = U+00F1, π = U+03C0, 漢 = U+6F22, 🔥 = U+1F525. Unicode ha catalogado más de 150,000 caracteres.

### 6.4 Code point vs codificación

Una distinción importante: el code point es abstracto (qué número le corresponde al símbolo); la codificación es concreta (cómo se almacena ese número en memoria). Las codificaciones más comunes:

- UTF-32: cada code point ocupa exactamente 4 bytes. Acceso directo a cualquier carácter por índice, pero costoso en espacio.
- UTF-16: 2 bytes para code points hasta U+FFFF, 4 bytes para los demás.
- UTF-8: longitud variable, entre 1 y 4 bytes. Los caracteres ASCII ocupan exactamente 1 byte, lo que da compatibilidad directa con texto en codificación antigua.

La cadena 'HOLA' ocupa 4 bytes en UTF-8 (1 byte por letra ASCII) y 16 bytes en UTF-32 (4 bytes por letra). Para texto predominantemente ASCII —código fuente, HTML, JSON— UTF-8 es ~4× más compacto. Esta ventaja explica su dominio en la web.

La composición completa que convierte un carácter en bytes es: símbolo → code point (Unicode) → secuencia de bytes (codificación). Son dos funciones distintas, ambas necesarias para almacenar texto.

## 7. Bits, bytes, palabras y memoria

### 7.1 Jerarquía

- Bit: unidad mínima, un elemento de {0,1}.
- Byte: cadena de 8 bits, por convención histórica. Tiene 2⁸ = 256 estados posibles.
- Palabra (word): ancho natural del procesador. En máquinas modernas, 64 bits = 8 bytes.

### 7.2 La palabra y la arquitectura del procesador

El tamaño de palabra es el ancho de los registros internos de la CPU. Define:

- El tamaño máximo de los operandos que la CPU procesa en una sola instrucción.
- El tamaño de las direcciones de memoria (los punteros).

Un procesador de 64 bits puede manejar nativamente hasta 2⁶⁴ ≈ 1.6 × 10¹⁹ direcciones de memoria distintas. Esto es del orden de 16 exabytes —cantidad muy superior a la RAM de cualquier sistema real—. La transición histórica de 32 a 64 bits fue impuesta cuando los 4 GB direccionables por 32 bits se volvieron insuficientes.

### 7.3 Direccionamiento por byte

La memoria moderna es direccionable por byte: cada dirección apunta a una celda de exactamente 1 byte, aunque la dirección misma sea una palabra de 8 bytes. La asimetría es intencional:

- Granularidad: los datos del programa tienen tamaños diversos (1 byte para un carácter ASCII, 2 para un entero corto, 4 para uno estándar, 8 para un puntero). Direccionar al byte permite manipular cualquier tipo sin operaciones extra de enmascarado y desplazamiento.
- Eficiencia real: aunque el espacio de direcciones de 64 bits permita 16 exabytes, en la práctica solo una fracción mínima se usa. El 'desperdicio' es nominal.

El sistema usa punteros grandes (8 bytes) que apuntan a celdas pequeñas (1 byte). El costo del puntero es bajo comparado con la complejidad que tendría no poder acceder a bytes individuales.

### 7.4 Atomicidad

Una operación es atómica si la CPU la ejecuta en una sola instrucción, sin descomponerla en pasos observables. Que una operación sea atómica depende de dos condiciones independientes:

- Tamaño de los operandos. Cada operando debe caber en una palabra. Sumar dos enteros de 128 bits en un procesador de 64 bits requiere varias instrucciones, propagando el carry manualmente.
- Aridad compatible con las instrucciones disponibles. Las operaciones aritméticas estándar son binarias: reciben exactamente dos operandos. Sumar tres números, aunque cada uno quepa en un registro, requiere dos instrucciones ADD encadenadas.

La ALU del procesador es binaria por construcción: su sumador físico tiene dos entradas de tamaño-de-palabra y una salida. Existen instrucciones especializadas que operan sobre fragmentos menores (cargar 1 byte, 2 bytes, 4 bytes) y también sobre datos más amplios (SIMD: 128, 256 o 512 bits a la vez). Pero la palabra sigue siendo el ancho de referencia.

## 8. Hilo conductor de la fase

La cadena lógica que conecta todos los temas anteriores:

La fase parte de una estructura algebraica abstracta —el álgebra booleana sobre {0,1}— ya familiar al estudiante en su forma más general (𝒫(X) con unión, intersección, complemento). De ahí se desciende un nivel: esa álgebra se materializa físicamente como compuertas, circuitos cuyo comportamiento eléctrico reproduce las tablas de verdad. Un solo operador —NAND— resulta ser funcionalmente completo: con suficientes compuertas NAND se construye cualquier función booleana imaginable.

Las funciones booleanas implementan dos cosas críticas: aritmética (sumadores construidos a partir de XOR y AND, resta vía complemento a dos) y representación de información (números naturales en cualquier base; texto vía Unicode y sus codificaciones). Esas operaciones se organizan dentro del procesador en registros del ancho de palabra, y la memoria que las nutre se direcciona por bytes con punteros del tamaño de la palabra.

Las restricciones de atomicidad —operaciones de una sola instrucción— vienen de dos límites físicos: el ancho de los registros y la aridad binaria del sumador. Más allá de esos límites, el procesador encadena instrucciones.

En última instancia, todo el aparato está sostenido por miles de millones de transistores —interruptores eléctricos microscópicos— conmutando billones de veces por segundo. La cadena causal completa va del transistor a la abstracción semántica del texto. Esa cadena es lo que la Fase 0 establece como base estructural para todo lo que sigue.

## Apéndice A — Ejercicios resueltos

Esta sección recoge los ejercicios resueltos durante las sesiones, en el orden en que se trabajaron. Cada uno incluye el enunciado, la solución y la justificación.

### A.1 Álgebra booleana

#### Ejercicio 1 — Evaluación de una expresión booleana

**Enunciado:** Evalúa ¬(x · ¬y) + (¬x · y) para x = 1, y = 0.

**Solución:**

```
¬y = ¬0 = 1
x · ¬y = 1 · 1 = 1
¬(x · ¬y) = ¬1 = 0

¬x = ¬1 = 0
¬x · y = 0 · 0 = 0

Resultado: 0 + 0 = 0
```

#### Ejercicio 2 — Tabla de verdad e identificación de la operación

**Enunciado:** Construye la tabla de verdad completa de ¬(x · ¬y) + (¬x · y) e identifica la operación lógica que representa.

| **x** | **y** | **Resultado** |
|---|---|---|
| 0 | 0 | 1 |
| 0 | 1 | 1 |
| 1 | 0 | 0 |
| 1 | 1 | 1 |

La tabla coincide con la implicación material x → y: solo es falsa cuando el antecedente es verdadero y el consecuente es falso.

#### Ejercicio 3 — Demostración algebraica sin tabla de verdad

**Enunciado:** Demuestra que ¬(x · ¬y) + (¬x · y) = ¬x + y usando únicamente axiomas del álgebra de Boole.

**Solución:**

```
¬(x · ¬y) + (¬x · y)
  = (¬x + y) + (¬x · y)        [De Morgan: ¬(A·B) = ¬A + ¬B; ¬¬y = y]
  = ¬x + y + ¬x · y
  = ¬x + y · (1 + ¬x)           [factorización de y]
  = ¬x + y · 1                  [identidad 1 + A = 1]
  = ¬x + y                      ∎
```

#### Ejercicio 4 — Expresar XOR con AND, OR, NOT

**Enunciado:** Expresa XOR usando únicamente AND, OR y NOT.

**Solución:**

```
XOR(x, y) = (x · ¬y) + (¬x · y)
```

### A.2 Completitud funcional

#### Ejercicio 5 — Expresar NOT con NAND

**Enunciado:** Expresa NOT(x) usando únicamente NAND.

**Solución:**

```
NOT(x) = NAND(x, x) = ¬(x · x) = ¬x

Paso clave: idempotencia (x · x = x).
```

#### Ejercicio 6 — Expresar AND con NAND

**Enunciado:** Expresa AND(x, y) usando únicamente NAND y verifica con la tabla de verdad para (1,1) y (1,0).

**Solución:**

```
AND(x, y) = NOT(NAND(x, y)) = NAND(NAND(x, y), NAND(x, y))

Verificación:
  (1,1): NAND(NAND(1,1), NAND(1,1)) = NAND(0, 0) = 1   ✓
  (1,0): NAND(NAND(1,0), NAND(1,0)) = NAND(1, 1) = 0   ✓
```

#### Ejercicio 7 — Expresar NOR usando solo NAND

**Enunciado:** Expresa NOR(x, y) usando únicamente NAND.

**Solución:**

```
NOR(x, y) = ¬(x + y)

Usando NOT(A) = NAND(A, A):
  NOR(x, y) = NAND(x + y, x + y)

Reemplazando OR por su expresión NAND, OR(x,y) = NAND(NAND(x,x), NAND(y,y)):

  NOR(x, y) = NAND(
    NAND(NAND(x,x), NAND(y,y)),
    NAND(NAND(x,x), NAND(y,y))
  )
```

### A.3 Representación posicional

#### Ejercicio 8 — Conversión 0xA3 a binario

**Enunciado:** Convierte 0xA3 a binario sin pasar por decimal.

**Solución:**

```
A → 1010
3 → 0011

Concatenando: 0xA3 = 1010 0011
```

#### Ejercicio 9 — Conversión 0xA3 a decimal y verificación

**Enunciado:** Convierte 0xA3 a decimal por expansión posicional y verifica que el binario obtenido da el mismo valor.

**Solución:**

```
Por hex:    0xA3 = 10·16¹ + 3·16⁰ = 160 + 3 = 163

Por binario: 1010 0011
  = 1·2⁷ + 0·2⁶ + 1·2⁵ + 0·2⁴ + 0·2³ + 0·2² + 1·2¹ + 1·2⁰
  = 128 + 32 + 2 + 1
  = 163   ✓
```

#### Ejercicio 10 — Bits por dígito octal

**Enunciado:** ¿Cuántos bits requiere cada dígito octal? Justifica por qué la concatenación con binario funciona.

**Solución:**

Octal tiene 8 dígitos posibles ({0..7}). Con 3 bits se obtienen 2³ = 8 combinaciones, exactamente las necesarias. Por tanto cada dígito octal ↔ 3 bits.

Para un número octal XY: XY = X·8 + Y = X·2³ + Y. Si X = a·2² + b·2 + c y Y = l·2² + m·2 + n, entonces X·2³ desplaza los bits de X a las posiciones 2⁵, 2⁴, 2³, sin traslapar las posiciones 2², 2¹, 2⁰ ocupadas por Y. La concatenación preserva la estructura posicional. La regla general: si b = 2^k, cada dígito en base b consume k bits y la concatenación es legítima.

#### Ejercicio 11 — Conversión de 'G' a hex y binario

**Enunciado:** Si 'A' = 0x41 en ASCII y las letras son consecutivas, ¿cuánto vale 'G' en hex y binario?

**Solución:**

```
'A' = 0x41
'B' = 0x42
...
'G' = 0x47

En binario: 4 → 0100, 7 → 0111
  'G' = 0100 0111
```

### A.4 Aritmética binaria y complemento a dos

#### Ejercicio 12 — Suma binaria 0xA3 + 0x1D

**Enunciado:** Suma 0xA3 + 0x1D en binario y verifica el resultado en decimal.

**Solución:**

```
0xA3 = 1010 0011
0x1D = 0001 1101
        ---------
       1100 0000  = 0xC0

Verificación:
  0xA3 = 163,  0x1D = 29,  163 + 29 = 192
  0xC0 = 12·16 + 0 = 192   ✓
```

#### Ejercicio 13 — Resta binaria 0xC0 − 0x1D

**Enunciado:** Calcula 0xC0 − 0x1D en binario usando borrow directo.

**Solución:**

```
0xC0 = 1100 0000
0x1D = 0001 1101

Restando bit a bit desde la derecha:
  bit 0: 0 − 1 → pedir préstamo → 10 − 1 = 1
  bit 1: (con préstamo) 0 − 0 − 1 → pedir préstamo → 1
  bit 2: (con préstamo) 0 − 1 − 1 → pedir préstamo → 0
  bit 3: (con préstamo) 0 − 1 − 1 → pedir préstamo → 0
  bit 4: (con préstamo) 0 − 0 − 1 → pedir préstamo → 1
  bit 5: (con préstamo) 0 − 0 − 1 → pedir préstamo → 0
  bit 6: (con préstamo) 1 − 0 − 1 = 0
  bit 7: 1 − 0 = 1

Resultado: 1010 0011 = 0xA3 = 163   ✓
```

#### Ejercicio 14 — Resta vía complemento a dos

**Enunciado:** Calcula 0xC0 − 0x1D usando complemento a dos.

**Solución:**

```
0x1D = 0001 1101

Complemento a dos de 0x1D (negativo en 8 bits):
  invertir: 1110 0010
  sumar 1:  1110 0011  = −29

Suma 0xC0 + (−0x1D):
   1100 0000
 + 1110 0011
 -----------
 1 1010 0011

El bit 9 (carry final) se descarta —no cabe en 8 bits—.
Resultado: 1010 0011 = 0xA3 = 163   ✓
```

#### Ejercicio 15 — Rango de 8 bits en complemento a dos

**Enunciado:** Determina el rango de enteros representables en 8 bits usando complemento a dos.

**Solución:**

```
Mayor positivo:  0111 1111 = +127  (bit de signo = 0)
Menor negativo:  1000 0000 = −128  (bit de signo = 1)

Rango: −128 ≤ x ≤ 127, es decir −2⁷ ≤ x ≤ 2⁷ − 1.

Generalización (n bits): −2^(n−1) ≤ x ≤ 2^(n−1) − 1.
```

#### Ejercicio 16 — Punto fijo de la negación

**Enunciado:** Calcula el complemento a dos de 1000 0000 (−128 en 8 bits). ¿Qué obtienes?

**Solución:**

```
1000 0000
  invertir: 0111 1111
  sumar 1:  1000 0000

El complemento a dos de −128 es él mismo. La operación de negación tiene
un punto fijo no trivial, lo cual rompe la estructura de grupo del conjunto
representable. No existe +128 en 8 bits.
```

### A.5 Codificación de texto

#### Ejercicio 17 — 'HOLA' en UTF-8 y UTF-32

**Enunciado:** Si 'A' = U+0041 ocupa 1 byte en UTF-8 y 4 bytes en UTF-32, ¿cuánto pesa la cadena 'HOLA' en cada codificación?

**Solución:**

```
'HOLA' tiene 4 caracteres ASCII.

UTF-8:  4 × 1 byte =  4 bytes
UTF-32: 4 × 4 bytes = 16 bytes

Factor 4× a favor de UTF-8 para texto principalmente ASCII.
```

### A.6 Memoria, palabras y direccionamiento

#### Ejercicio 18 — Direcciones en 64 bits

**Enunciado:** ¿Cuántas direcciones distintas son posibles en un sistema de 64 bits? Expresa en potencias de 2 y aproxima en base 10.

**Solución:**

```
Cada dirección es una cadena de 64 bits → 2⁶⁴ direcciones distintas.

Aproximación en base 10:
  Atajo: 2¹⁰ ≈ 10³
  2⁶⁴ = 2⁶⁰ · 2⁴ ≈ (10³)⁶ · 16 = 10¹⁸ · 16 ≈ 1.6 × 10¹⁹

Del orden de 10¹⁹ direcciones.
```

#### Ejercicio 19 — Memoria total direccionable en GB

**Enunciado:** Convierte 2⁶⁴ bytes a gigabytes (1 GB ≈ 2³⁰ bytes) y aproxima en base 10.

**Solución:**

```
2⁶⁴ bytes / 2³⁰ (bytes/GB) = 2³⁴ GB

Aproximación:
  2³⁴ = 2³⁰ · 2⁴ ≈ 10⁹ · 16 ≈ 1.6 × 10¹⁰ GB

Del orden de 16 exabytes —magnitud excesiva para RAM real—.
```

### A.7 Transistores y compuertas

#### Ejercicio 20 — NAND con transistores

**Enunciado:** Si AND requiere dos transistores en serie y NOT uno solo configurado inverso, ¿cuántos transistores mínimo necesitas para construir NAND? Describe la disposición.

**Solución:**

Tres transistores. Dos en serie computan A · B; el tercero, configurado como NOT, va al final de la cadena e invierte la salida del AND. La posición del NOT es crítica: debe operar sobre el resultado del AND, no sobre una entrada individual (poner el NOT al principio produciría ¬A · B, función distinta a NAND).

Nota: en CMOS real, NAND se construye con cuatro transistores en configuración directa, sin necesidad de encadenar AND + NOT. Esta es una razón por la cual NAND es la pieza fundamental del hardware moderno.

#### Ejercicio 21 — NOR con transistores

**Enunciado:** Construye NOR usando la misma lógica metafórica. ¿Cuántos transistores y en qué configuración?

**Solución:**

Construcción óptima — tres transistores: dos en paralelo computan A + B en su salida común; el tercero, configurado como NOT, invierte la salida del OR. Es la imagen especular de NAND, con paralelo en lugar de serie.

Construcción alternativa vía De Morgan — cuatro transistores: aplicar ¬(A + B) = ¬A · ¬B. Construir cada NOT por separado (dos transistores) y luego un AND en serie (dos transistores más). Funciona, pero usa un transistor adicional.

Conclusión pedagógica: expresiones algebraicamente equivalentes pueden tener costos físicos distintos. La minimización lógica es el área que estudia cómo encontrar la expresión más barata para una función dada.

## Cierre

Esta fase establece la base estructural sobre la que descansan todas las fases posteriores. A partir de aquí, la Fase 1 estudiará la arquitectura del procesador: registros, ALU, ciclo fetch-decode-execute y Assembly básico. Los conceptos cubiertos en este reporte —representación, aritmética, palabra, atomicidad— serán la materia prima de esa siguiente etapa.

Criterio de salida cumplido: el estudiante puede razonar en binario y hexadecimal con fluidez, y comprende cómo la lógica booleana materializa operaciones matemáticas en hardware real.
