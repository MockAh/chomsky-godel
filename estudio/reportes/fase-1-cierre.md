**FASE 1 — REPORTE DE CIERRE**

La máquina desnuda: arquitectura

Estudiante: Guillermo

Programa: Ingeniería en Sistemas y Ciberseguridad

Fecha de cierre: 4 de octubre de 2026 (teoría) · 23 de noviembre de 2026 (reto de escritorio)

## Propósito de este documento

Este reporte cierra la Fase 1 del programa. Recoge los conceptos vistos, las correspondencias establecidas y los trazados resueltos durante las sesiones. Está pensado como referencia consultable: si en una fase posterior surge una duda sobre registros, el ciclo de ejecución, la jerarquía de memoria o el direccionamiento, este documento debe bastar para refrescar la base.

La estructura sigue el orden temático en que se desarrollaron las cápsulas, no el cronológico. La Sección 10 reúne la metáfora del taller construida durante la fase, que funcionó como lenguaje compartido y debe conservarse para fases posteriores. El Apéndice A recoge los trazados y ejercicios resueltos en sesión. El Apéndice B recoge el reto de cierre de escritorio: los ejemplos del Tutor y las respuestas finales del estudiante.

## 1. Arquitectura de la CPU

### 1.1 Las tres unidades centrales

Una CPU es un conjunto pequeño de unidades coordinadas por un reloj. Las tres que importan a este nivel:

- ALU (Unidad Aritmético-Lógica): ejecuta las operaciones aritméticas y booleanas. Es binaria por construcción: recibe exactamente dos operandos y produce un resultado.
- Registros: memoria interna de la CPU. Fijos en número y en tamaño. Es lo único sobre lo que la ALU opera directamente.
- Unidad de Control (UC): lee cada instrucción desde memoria, la decodifica y activa las líneas de control correspondientes.

### 1.2 La Unidad de Control no es programable

Punto estructural que conviene no perder: la UC no almacena instrucciones ni ejecuta un programa propio. Es un circuito — un autómata finito materializado con compuertas, las mismas de la Fase 0. Ante un patrón de bits (la instrucción leída), la red de compuertas activa unas líneas u otras. Reprogramar la UC equivaldría a rediseñar el chip.

En la correspondencia con la Máquina de Turing, la UC es la función de transición δ hecha hardware. Las instrucciones en memoria son el contenido de la cinta. La universalidad se obtiene cambiando la cinta, no la máquina.

### 1.3 El salto conceptual de la fase: la finitud

El espacio de trabajo real de la CPU es finito, nombrado y muy pequeño. No hay un conjunto infinito de variables disponibles: hay 16 huecos. Cada operación cuesta ciclos, cada dato tiene que viajar, y la distancia a la que vive un dato determina el costo de usarlo. Esta restricción es la que no tiene análogo en la práctica matemática abstracta, y es el reentrenamiento central de la fase.

## 2. Arquitectura de von Neumann

### 2.1 Instrucciones y datos comparten memoria

Las instrucciones no viven dentro de la CPU: viven en memoria, en el mismo espacio direccionable que los datos. No hay separación física entre ambos. Todo son bytes; la distinción entre "instrucción" y "dato" es de interpretación, no de ubicación.

Prácticamente toda computadora de uso general actual —PC, teléfono, servidor— es von Neumann. La alternativa, llamada arquitectura Harvard, mantiene memorias separadas para código y datos y sobrevive en microcontroladores y procesadores de señal. Dentro de la propia CPU, sin embargo, la caché L1 sí está separada en L1 de instrucciones y L1 de datos: von Neumann por fuera, Harvard por dentro.

### 2.2 Consecuencia estructural

Si nada en los bytes distingue código de datos, entonces la corrección de un programa depende enteramente de que el flujo de ejecución nunca aterrice donde no debe. Casi todo lo que se estudia en explotación de binarios es alguna forma de hacer que el puntero de instrucción aterrice en un lugar no previsto. Este punto se desarrolla en la Sección 6.3 y en la 7.4.

## 3. Registros y memoria

### 3.1 La distinción

Un registro es memoria interna de la CPU: 8 bytes (una palabra) en arquitectura de 64 bits, con nombre propio. Hay 16 de propósito general en x86-64, lo que da 16 × 8 = 128 bytes de espacio de trabajo verdaderamente inmediato.

|  | **Registro** | **Memoria (RAM)** |
|---|---|---|
| Cantidad | 16 de propósito general, fija | Miles de millones de celdas |
| Tamaño de celda | 8 bytes (1 palabra) | 1 byte |
| Identificación | Por nombre (rax, rbx, rcx…) | Por dirección (un número) |
| Acceso de la ALU | Directo | Imposible: hay que cargar primero |

La última fila es la operativa: la ALU no alcanza la memoria. Todo dato debe cargarse a un registro antes de ser operado.

### 3.2 El ciclo traer–operar–devolver

Operar sobre dos valores guardados en memoria exige tres clases de paso:

- Cargar ambos operandos de memoria a registros (obligatorio).
- Ejecutar la operación en la ALU, registro contra registro (obligatorio).
- Almacenar el resultado de vuelta en memoria (opcional).

El tercer paso es una decisión, no una necesidad: tras la operación el resultado ya está en un registro. Solo se devuelve a memoria si el valor debe persistir o si se necesita liberar el registro. Esa presión por liberar registros es consecuencia directa de que solo haya 16.

### 3.3 Tamaño del registro y tamaño de la variable

El registro mide exactamente una palabra; es fijo y físico. La variable puede ser menor: un carácter de 1 byte ocupa un registro de 8 y deja 7 sin usar. Si el dato es mayor que una palabra, no cabe en un registro y la operación debe descomponerse en varias instrucciones encadenadas, propagando el carry manualmente — el resultado sobre atomicidad establecido al cierre de la Fase 0.

### 3.4 Registros no visibles al programador

Además de los 16 de propósito general existen registros con función fija. Los que aparecieron en esta fase:

| **Registro** | **Qué guarda** | **Visible al programador** |
|---|---|---|
| rip | La dirección de la próxima instrucción | Indirectamente (vía saltos) |
| rflags | El resultado del último juicio de la ALU | Indirectamente (vía saltos condicionales) |
| rsp | La dirección de la cima del stack | Sí |
| IR (registro de instrucción) | La instrucción que se está decodificando | No: ninguna instrucción lo lee ni lo escribe |

## 4. Jerarquía de memoria

### 4.1 La tensión física

Pequeño-y-rápido y grande-y-lento están en tensión irreducible. Una memoria que se consulta de forma instantánea tiene que ser diminuta; una que guarda miles de millones de celdas ocupa espacio y por tanto está lejos. No existe una sola memoria que sea ambas cosas.

La solución no es elegir, sino apilar niveles: una secuencia de memorias intermedias, cada una más grande y más lenta que la anterior, que guardan copias de lo recientemente usado.

| **Nivel** | **Capacidad aproximada** | **Contenido** |
|---|---|---|
| Registros | 128 bytes | Solo datos en uso inmediato |
| Caché L1 | Decenas de KB | Separada: L1i (instrucciones) y L1d (datos) |
| Caché L2 / L3 | Cientos de KB a decenas de MB | Mixta: instrucciones y datos |
| RAM | Gigabytes | Código, datos, stack y heap del programa |
| Disco | Terabytes | Programas y archivos no cargados |

Nada se ejecuta desde el disco. Para ejecutar un programa, el sistema operativo copia primero su código a RAM.

### 4.2 Localidad: la apuesta del diseño

La jerarquía funciona porque los programas reales concentran sus accesos en regiones minúsculas del espacio total. Esa regularidad se llama localidad y tiene dos formas:

- Localidad temporal: lo que se usó hace poco se vuelve a usar pronto. Es pasiva: el dato simplemente se queda en caché en vez de volver a RAM.
- Localidad espacial: lo que está contiguo a lo que se usó se va a usar pronto. Es activa y especulativa: se suben datos que nadie ha pedido todavía.

Los bucles son lo que justifica la apuesta. Un bucle de diez instrucciones que itera un millón de veces lee las mismas diez instrucciones y toca las mismas pocas variables en cada vuelta. Se traen una vez y se quedan.

Es importante que esto no es una ley: es una regularidad empírica. Un programa que salte a direcciones aleatorias en todo el espacio de direcciones es perfectamente legal y arruina la caché por completo. El hardware está optimizado para una distribución típica, no para el caso peor.

### 4.3 La línea de caché

La caché nunca trae un byte suelto: trae un bloque contiguo de tamaño fijo, llamado línea de caché. En x86-64 son 64 bytes. Se pide un byte y suben los 64 bytes del bloque que lo contiene.

La razón es de costo: el viaje es lo caro, no la carga. Un trayecto a RAM cuesta prácticamente lo mismo trayendo un byte que trayendo sesenta y cuatro. Si ya se hizo el viaje, conviene llenarse los brazos.

Esto hay que distinguirlo del prefetch, que es un mecanismo separado: la CPU detecta que se está recorriendo memoria en orden y manda traer los bloques siguientes antes de necesitarlos. La línea de caché es transporte automático y ciego; el prefetch es predicción y puede fallar.

### 4.4 Consecuencia práctica

Un arreglo recorrido en orden consecutivo aprovecha cada línea de caché para varios accesos seguidos. El mismo arreglo recorrido a saltos grandes provoca un viaje nuevo en cada acceso y desperdicia la mayor parte de cada línea traída. Mismo algoritmo, mismo número de operaciones, hasta un orden de magnitud de diferencia en tiempo real. El costo asintótico no captura esta diferencia.

Nota de seguridad, a desarrollar en fases posteriores: cuando el tiempo de ejecución depende de si un dato estaba en caché, ese tiempo filtra información sobre qué datos se tocaron. Es la base de una familia entera de ataques por canal lateral.

## 5. El ciclo fetch-decode-execute

### 5.1 Los cuatro pasos

Este es el paso de cómputo real de la máquina, y el núcleo de la fase.

- Fetch (buscar): rip contiene una dirección de memoria. La CPU trae los bytes que hay en esa dirección —casi siempre desde la caché L1 de instrucciones— y los sostiene en el registro de instrucción.
- Decode (decodificar): la Unidad de Control interpreta esos bytes y obtiene dos cosas a la vez: qué operación es, y cuántos bytes mide la instrucción.
- Execute (ejecutar): se activan las líneas correspondientes. La operación modifica un lugar: un registro de propósito general, rflags, o el propio rip.
- Avanzar: a rip se le suma la longitud obtenida en el decode, salvo que la instrucción ya lo haya reescrito ella misma.

Y vuelve al primer paso, indefinidamente, miles de millones de veces por segundo. La CPU no ve el programa: ve una instrucción, la ejecuta, y mira la siguiente.

### 5.2 Correspondencia con la Máquina de Turing

La correspondencia es exacta y es la conexión que esta fase tenía como objetivo establecer. No es analogía pedagógica: es la misma estructura formal, materializada.

| **Máquina de Turing** | **CPU real** |
|---|---|
| Cinta | Memoria direccionable |
| Posición del cabezal | rip |
| Estado interno | Registros + rflags |
| Función de transición δ | Unidad de Control (circuito) |
| Un paso de cómputo | Un ciclo fetch-decode-execute |

Con las dos diferencias que definen esta fase: δ es una función abstracta, la UC es un circuito finito; la cinta es infinita, la memoria no.

### 5.3 Longitud variable y decodificación

En x86 las instrucciones tienen longitud variable: entre 1 y 15 bytes. No hay separadores ni marcas de fin. La longitud está implícita en el opcode: al decodificar los primeros bytes, el circuito ya sabe cuántos bytes más pertenecen a esa instrucción.

En términos de lenguajes formales, la decodificación funciona como un código de prefijo: ningún opcode válido es prefijo de otro, y por eso el flujo de bits se parsea sin ambigüedad y sin delimitadores. La unicidad queda garantizada siempre que se entre por un punto de inicio correcto.

## 6. Control de flujo: saltos y banderas

### 6.1 El salto incondicional

Un salto es una instrucción que, en su fase de ejecución, escribe directamente una dirección en rip en vez de dejar que se le sume la longitud. La dirección destino va codificada dentro de la instrucción misma.

Un bucle no existe como entidad en el hardware. Es únicamente un rip al que se le escribió una dirección anterior. La estructura la ve el programador; la CPU solo ve una dirección.

### 6.2 Banderas y salto condicional

La ALU deposita en rflags señales sobre el resultado de su última operación: si dio cero (ZF), si hubo carry, el signo, si hubo desbordamiento. En esta fase el relevante es ZF:

- Resultado igual a cero → ZF = 1
- Resultado distinto de cero → ZF = 0

La instrucción cmp a, b resta a − b y descarta el resultado: su único efecto es dejar las banderas puestas. Si los operandos son iguales, la resta da cero y ZF queda en 1.

La instrucción je destino (jump if equal) lee rflags antes de actuar. Si ZF = 1, escribe la dirección destino en rip. Si ZF = 0, no hace nada y rip avanza normalmente.

Conviene separar las tres piezas, porque es donde se concentró la confusión durante la sesión: je es la orden; el destino es un renglón concreto escrito dentro de la propia instrucción; ZF es la condición, que vive en rflags y no es un destino. Hay dos destinos posibles —el escrito en la instrucción y el renglón siguiente— y una sola pregunta que decide entre ellos.

La división del trabajo queda así: la ALU juzga, rflags recuerda el juicio, el salto condicional lo obedece.

### 6.3 Instrucciones desalineadas

Dado que la longitud solo se conoce al decodificar, y que no hay marca de inicio en los bytes, la CPU no tiene forma de detectar que está leyendo desde la mitad de una instrucción. Si rip apunta al tercer byte de una instrucción de cinco, la UC decodifica ese byte como un opcode —que probablemente sea válido—, ejecuta lo que signifique, avanza según esa longitud y continúa. Sin error y sin aviso.

El resultado es un programa completamente distinto: instrucciones reales que nadie escribió, emergidas de leer los mismos bytes con otro alineamiento. La instrucción no es una propiedad de los bytes; es una propiedad de los bytes más el punto donde se empezó a leer.

Esto es una técnica ofensiva real: esconder instrucciones dentro de otras, de modo que un analista que lee el programa desde el principio vea código inocuo mientras el atacante hace aterrizar rip a mitad de una instrucción. En arquitecturas de longitud fija —ARM, RISC-V, con instrucciones de 4 bytes— esto es imposible, porque solo hay un alineamiento válido.

## 7. Organización de la memoria de un programa

### 7.1 Las regiones

La memoria de un programa no es una masa indiferenciada de celdas: está dividida en regiones con reglas distintas.

| **Región** | **Qué contiene** | **Disciplina** |
|---|---|---|
| Código | Las instrucciones del programa | Solo lectura |
| Datos estáticos | Lo que existe desde el arranque | Tamaño y posición fijos |
| Stack (pila) | Direcciones de retorno, variables locales | LIFO, automática |
| Heap (montón) | Memoria pedida explícitamente | Sin orden, gestión manual |

### 7.2 El stack y rsp

El stack es una zona de la RAM, no una pieza de hardware. Su parte activa vive de hecho en caché, porque la cima se toca constantemente y la localidad temporal actúa sola — pero la caché no sabe qué es un stack; solo retiene lo reciente.

Tiene su propio puntero: rsp marca siempre la dirección de la cima. El patrón se repite: rip marca dónde va la ejecución en el código; rsp marca dónde va la pila.

### 7.3 Por qué la disciplina LIFO

La estructura LIFO no es una elección de conveniencia: es lo que el anidamiento exige. En cualquier proceso donde para terminar A hay que suspenderlo, hacer B y volver exactamente al punto donde se dejó A, el orden de retorno es forzosamente el inverso del orden de entrada. Si B a su vez suspende para hacer C, entonces C debe terminar antes que B, y B antes que A.

Los ejemplos familiares son los paréntesis anidados —cuyo reconocimiento requiere exactamente un autómata de pila— y las demostraciones que suspenden un teorema para probar un lema. En la CPU, el caso es la llamada a función: el programa suspende lo que hacía, salta a otro lugar, y debe volver a la instrucción siguiente. El stack guarda las direcciones de retorno.

### 7.4 Semilla para la Fase 2

La dirección de retorno está guardada en el stack, en memoria, mezclada con datos que el programa escribe. La CPU la obedece sin verificarla: no hay comprobación de que sea una dirección legítima.

Si un dato mal dimensionado se escribe más allá de su espacio y encima de la dirección de retorno, el caso más probable es que el programa salte a una dirección inválida y el sistema lo termine. Ese es el caso benigno. Si en lugar de basura se escribe una dirección cuidadosamente elegida, el programa no falla: retorna a donde el atacante decidió. Ese es el buffer overflow, y es la razón de que exista la Fase 2.

## 8. Direccionamiento e indirección

### 8.1 Qué es una dirección

La memoria es una secuencia de celdas numeradas, cada una de 1 byte. Una dirección es simplemente el número de la celda. Un dato de 8 bytes ocupa 8 celdas consecutivas y se nombra por el número de la primera.

Formalmente, la memoria es una función total sobre un dominio finito:

```
f : D -> {0,1}^8     con D subconjunto finito de N
```

El punto crítico es que una dirección es un número natural. Por tanto cabe en un registro, igual que cualquier otro dato. Se puede poner en la mesa de trabajo el número de una celda en lugar del contenido de esa celda.

### 8.2 La indirección

Para formular la indirección correctamente hace falta leer una palabra completa, no un byte, porque una dirección de 64 bits no cabe en un byte. Defínase la lectura de palabra:

```
F(x) = < f(x), f(x+1), ..., f(x+7) >   interpretado como natural
 
F : D -> N
```

Ahora los tipos cierran: la salida de F es un natural, y las direcciones son naturales, de modo que F(F(x)) está bien definida. Lo que expresa es dos lecturas encadenadas: F(x) entrega un número que se interpreta como dirección, y F de ese número entrega el contenido real.

Ejemplo concreto: si la celda 200 contiene el valor 7000, y la celda 7000 contiene el valor 42, entonces F(200) = 7000 y F(F(200)) = 42. La celda 200 no guarda el dato: guarda dónde está el dato.

La composición se puede encadenar indefinidamente —F(F(F(x)))— porque nada en los bytes distingue un número-dato de un número-dirección. La interpretación la pone el programa, no la memoria. Un puntero es un número que alguien decidió usar como índice en vez de como valor.

### 8.3 Para qué sirve

- Objetos que no caben: un dato de 10 000 bytes no entra en un registro, pero su dirección sí ocupa exactamente 8 bytes. Cabe la referencia aunque no quepa el objeto.
- Compartir sin copiar: dos partes del programa que guardan la misma dirección ven el mismo dato. Una escribe, la otra lo observa, sin duplicación.
- Estructuras encadenadas: si cada elemento guarda la dirección del siguiente, se construyen listas, árboles y grafos. Lo que en matemáticas se define por relaciones, aquí se construye con direcciones.

Esta sección es el cimiento conceptual directo de los punteros de C, que se trabajan en la Fase 2.

## 9. Assembly x86 básico

### 9.1 Sintaxis

En sintaxis Intel, la forma general es:

```
verbo   destino, origen
```

El primer operando es a dónde va el resultado; el segundo es el valor que entra. Así, mov rax, 5 coloca el valor 5 en rax. En las instrucciones aritméticas el destino es también el primer operando: sub rax, rbx calcula rax = rax − rbx.

### 9.2 Los corchetes: la indirección como notación

| **Escrito** | **Significa** |
|---|---|
| rax | El registro rax; su contenido se usa como valor |
| [rax] | La celda de memoria cuya dirección está en rax |

Los corchetes son exactamente la composición F(F(x)) de la sección anterior, ya como notación. La dirección del flujo la decide de qué lado está el corchete: mov rbx, [rax] lee de memoria; mov [rax], rbx escribe en memoria. Mismo verbo, operación inversa.

### 9.3 Instrucciones trabajadas en esta fase

| **Instrucción** | **Qué hace** | **Qué modifica** |
|---|---|---|
| mov d, o | Copia el valor de o en d | Un registro o una celda de memoria |
| add d, o | d = d + o | d y rflags |
| sub d, o | d = d − o | d y rflags |
| dec d | d = d − 1 | d y rflags |
| cmp a, b | Resta a − b y descarta el resultado | Solo rflags |
| jmp destino | Salta siempre | rip |
| je destino | Salta solo si ZF = 1 | rip (condicionalmente) |
| hlt | Detiene la ejecución | — |

Nota: dec y sub dejan las banderas puestas por sí solas, de modo que un cmp posterior contra cero es redundante en la práctica. En los trazados de esta fase se mantuvo explícito para separar con claridad el acto de juzgar del acto de obedecer el juicio.

## 10. La metáfora del taller

Durante la fase se construyó una metáfora sostenida que funcionó como lenguaje compartido. Se registra aquí completa porque conviene conservarla para las fases siguientes.

| **En el taller** | **En la máquina** |
|---|---|
| El carpintero | Unidad de Control + ALU |
| La hoja de instrucciones | El código del programa, en memoria |
| El dedo sobre el renglón | rip |
| La mano que sostiene el renglón | Registro de instrucción (IR) |
| Los 16 huecos de la mesa | Registros de propósito general |
| La libreta al margen | rflags |
| La repisa pegada a la mesa | Caché L1 (separada: hoja y piezas) |
| Las estanterías de la habitación | Caché L2 y L3 |
| El almacén | RAM |
| La bodega lejana | Disco |
| Las piezas | Los datos |
| La pila de hojas dejadas boca abajo | Stack |
| La marca sobre la hoja de encima | rsp |

Las acciones, en el mismo lenguaje: mov es traer una pieza del almacén a la mesa o devolverla; cmp es medir dos piezas y anotar el resultado en la libreta, sin cortar nada; jmp es mover el dedo a otro renglón, siempre; je es mirar la libreta primero y mover el dedo solo si dice que coincidieron.

Dos cosas que la metáfora vuelve evidentes. Primero, que la hoja de instrucciones también vive en el almacén, de modo que hoja y piezas compiten por el mismo camino: eso es von Neumann. Segundo, que el carpintero nunca lee la hoja completa — lee un renglón, lo ejecuta, mira el siguiente, y no sabe que existe un bucle; solo sabe que a veces el dedo va hacia atrás.

## 11. Hilo conductor de la fase

La Fase 0 terminó con una ALU abstracta: un sumador binario sobre palabras, sin contexto físico. La Fase 1 abre esa caja y la rodea del aparato que la alimenta.

La CPU resulta ser tres unidades: una ALU que opera, unos registros que sostienen los operandos, y una Unidad de Control que no es un programa sino un circuito —la función de transición de Turing hecha silicio—. Las instrucciones que esa UC ejecuta no viven en ella, sino en memoria, indistinguibles de los datos: eso es von Neumann, y de ahí se desprende que la corrección de un programa dependa enteramente de dónde aterrice el puntero de instrucción.

Como la ALU solo alcanza los registros y estos son apenas 128 bytes, todo dato debe viajar. Y como pequeño-y-rápido y grande-y-lento son incompatibles, el viaje se abarata apilando niveles de caché que apuestan por la localidad de los programas reales. La unidad de transporte es la línea de 64 bytes, porque lo caro es ir y no cargar.

Sobre esa base se monta el ciclo fetch-decode-execute, que es el paso de cómputo real de la máquina. Su cuarto paso —avanzar rip— es el que los saltos interceptan: escribir en rip es todo lo que hace falta para producir bucles y condicionales, con rflags como memoria del último juicio de la ALU.

La memoria, finalmente, no es homogénea: tiene regiones con disciplinas distintas, y la del stack es LIFO porque el anidamiento no admite otra. Y como una dirección es un número que cabe en un registro, se puede guardar la referencia de lo que no cabe — la indirección, que es el cimiento de los punteros.

La cadena completa de la fase va del registro al salto: del espacio finito de trabajo a la capacidad de redirigir la ejecución. Ambos extremos reaparecen en la Fase 2, cuando C dé nombres a estos objetos y los buffer overflows muestren qué ocurre cuando los dos se cruzan.

## Apéndice A — Trazados y ejercicios resueltos

Esta sección recoge los ejercicios resueltos durante las sesiones, en el orden en que se trabajaron.

### A.1 Trazado de un fragmento aritmético con salto

**Enunciado:** traza el siguiente fragmento, indicando el valor de los registros tras cada instrucción, el estado de ZF y si el salto se toma.

```
mov  rax, 10
mov  rbx, 3
sub  rax, rbx
cmp  rax, 7
je   iguales
```

**Solución:**

```
mov  rax, 10    -> rax = 10
mov  rbx, 3     -> rax = 10,  rbx = 3
sub  rax, rbx   -> rax = 7,   rbx = 3
cmp  rax, 7     -> 7 - 7 = 0  ->  ZF = 1  (resultado descartado)
je   iguales    -> ZF = 1  ->  SALTA
```

Justificación: cmp no modifica rax; su único efecto observable es dejar ZF en 1 porque la resta dio cero. je lee esa bandera y escribe en rip la dirección de la etiqueta iguales.

### A.2 Trazado con indirección

**Enunciado:** traza el siguiente fragmento. Estado inicial: la celda de memoria 200 contiene el valor 41.

```
mov  rax, 200
mov  rbx, [rax]
add  rbx, 1
mov  [rax], rbx
```

**Solución:**

```
mov  rax, 200     -> rax = 200   (una direccion, no un dato)
mov  rbx, [rax]   -> lee la celda 200  ->  rbx = 41
add  rbx, 1       -> rbx = 42
mov  [rax], rbx   -> escribe 42 en la celda 200
 
Estado final:  rax = 200,  rbx = 42,  celda 200 = 42
```

Justificación: el fragmento ejecuta el ciclo completo traer–operar–devolver en cuatro instrucciones. El valor 41 no es un destino: es el contenido anterior de la celda, que queda sobrescrito. La asimetría de los corchetes es lo que invierte la dirección del flujo entre la segunda y la cuarta instrucción.

### A.3 Construcción de un bucle

**Enunciado:** con un contador en rcx inicializado en 3, construye un bucle que repita hasta que el contador llegue a cero.

**Solución:**

```
bucle:  dec  rcx
        cmp  rcx, 0
        je   fin
        jmp  bucle
fin:    hlt
```

**Traza completa:**

```
vuelta 1:  dec -> rcx = 2   cmp -> ZF = 0   je no salta   jmp -> bucle
vuelta 2:  dec -> rcx = 1   cmp -> ZF = 0   je no salta   jmp -> bucle
vuelta 3:  dec -> rcx = 0   cmp -> ZF = 1   je SALTA -> fin
           hlt
```

Observación estructural: no hay ninguna entidad "bucle" en el hardware. La repetición es únicamente el efecto de que jmp escriba en rip una dirección anterior. Y el bucle entero —cinco instrucciones— cabe holgadamente en una línea de caché, de modo que se trae una sola vez de memoria y se ejecuta desde la caché L1 en todas las vueltas restantes.

### A.4 Ejercicios conceptuales resueltos en sesión

**Ejercicio 1 — Capacidad del espacio de trabajo.** ¿Qué ocurre cuando un programa tiene 200 variables vivas simultáneamente?

Caben 16 en los registros. Las 184 restantes permanecen en memoria, y el programa alterna cargas y almacenamientos para mantener a mano las que necesita en cada momento. La presión por liberar registros es la consecuencia directa de la finitud.

**Ejercicio 2 — Qué paso del ciclo traer–operar–devolver puede omitirse.**

El tercero. Tras la operación el resultado ya está en un registro; devolverlo a memoria solo es necesario si debe persistir o si hace falta liberar el registro. Los dos primeros son obligatorios porque la ALU no alcanza la memoria.

**Ejercicio 3 — Qué trae la caché cuando va a memoria, y por qué.**

Un bloque contiguo de 64 bytes, no el byte pedido. La justificación es que el costo dominante es el trayecto, no el volumen transportado; y la apuesta de localidad espacial dice que los vecinos se van a pedir pronto.

**Ejercicio 4 — Qué ocurre si rip aterriza a mitad de una instrucción.**

No se detiene ni señala error. La CPU no puede detectarlo: decodifica ese byte como opcode, ejecuta lo que signifique y continúa. Produce un programa distinto a partir de los mismos bytes. La respuesta inicial del estudiante —que el procesador identificaría el desfase y se recuperaría— es la intuición natural y es precisamente la que el hardware no cumple.

**Ejercicio 5 — Qué proceso de cómputo exige disciplina LIFO.**

El anidamiento. Siempre que un proceso se suspende para ejecutar otro y debe retomarse en el punto exacto donde quedó, el orden de retorno es el inverso del de entrada. Los paréntesis balanceados son el caso formal; la llamada a función es el caso de la máquina.

**Ejercicio 6 — Qué se gana guardando en un registro la dirección de un dato en vez del dato.**

Que cabe la referencia aunque no quepa el objeto: una dirección ocupa exactamente una palabra, sea cual sea el tamaño de lo que apunta. Además permite compartir un mismo dato sin copiarlo y encadenar estructuras donde cada elemento guarda la dirección del siguiente.

## Apéndice B — Reto de cierre de escritorio: «Del trazado a la ejecución»

Enunciado: `estudio/retos/fase-1-reto-cierre.md`. Trabajo del estudiante: `retos/fase-1/`. Se hizo en WSL
(x86-64 nativo) entre el 2026-11-20 y el 2026-11-23. Cada mini-tarea registra el ejemplo que dio el Tutor
y la respuesta final del estudiante. El detalle de cada sesión, con todas las preguntas, está en
`estudio/sesiones/`.

### B.1 Mini-tarea 1 — Preparar el taller (2026-11-20)

**Objetivo:** tener `nasm`, `ld` y `gdb` funcionando en x86-64.

**Respuesta final del estudiante:** instaló todo él mismo (`sudo apt install -y nasm gdb`) y verificó:

```
x86_64
NASM version 2.16.01
GNU ld (GNU Binutils for Ubuntu) 2.42
GNU gdb (Ubuntu 15.1-1ubuntu1~24.04.1) 15.1
```

Lección práctica: en bash, `!` delante de un comando niega su código de salida. Ese `!` solo sirve en el
prompt de Claude Code, y el error fue del Tutor al darle el comando así.

### B.2 Mini-tarea 2 — Primer programa verificable (2026-11-20)

**Concepto:** una máquina real no tiene «fin de hoja». Para terminar, el programa toca la puerta del
dueño (`syscall`) con `rax = 60` (trámite: terminar) y `rdi` = código de salida.

**Ejemplo del Tutor:**

```nasm
global _start
section .text
_start:
    mov rax, 60     ; trámite: terminar
    mov rdi, 68     ; código de salida
    syscall
```

**Respuesta final del estudiante** (`retos/fase-1/mt2.asm`): el mismo esqueleto con `rdi = 42`, correcto
a la primera. Salida verificada: `42`.

**Ejercicio de finitud:** con `rdi = 300` predijo 300 y salió **44**. Tras la explicación (el código de
salida cabe en un byte: 300 mod 256 = 44) predijo él solo, y verificó, **256 → 0** y **511 → 255**.

**Ejercicio de control (etiqueta = dirección):** en el desensamblado de un programa de juguete con
`jmp fin`, identificó correctamente el renglón que el dedo nunca toca (`401007`).

### B.3 Mini-tarea 3 — Traducir el trazado A.1 (2026-11-20 y 2026-11-22)

**Concepto:** cada camino debe terminar con su propio `syscall`; si no, se derrama en el siguiente. El
código de salida es el testigo del camino que tomó la CPU.

**Ejemplo del Tutor** (A.1 en código real; sale con 1):

```nasm
global _start
section .text
_start:
    mov  rax, 10
    mov  rbx, 3
    sub  rax, rbx       ; rax = 7
    cmp  rax, 7         ; 7 − 7 = 0 → ZF = 1
    je   iguales        ; salta

    mov  rax, 60        ; camino «no saltó»
    mov  rdi, 0
    syscall

iguales:                ; camino «saltó»
    mov  rax, 60
    mov  rdi, 1
    syscall
```

**Respuesta final del estudiante** (ejercicio equivalente, solo, `retos/fase-1/mt3.asm`):

```nasm
global _start
section .text
_start:
    mov  rax, 20
    mov  rbx, 6
    sub  rax, rbx
    cmp  rax, 14
    je   iguales

    mov rax, 60
    mov rdi, 0
    syscall

iguales:
    mov rax, 60
    mov rdi, 1
    syscall
```

- Predicción con `cmp rax, 15`: «rax = 14; ¿son iguales 15 y rax? No. Ergo, ZF = 0, ergo, no hay salto;
  el programa termina con código 0». Verificado: `0`.
- Con `cmp rax, 14` (versión final del archivo): verificado `1`. Lo corrió antes de predecir; se le
  señaló.
- Pregunta de cierre: ¿qué otras marcas enciende 14 − 15 = −1? No lo supo. Respuesta: **SF = 1**
  (negativo) y **CF = 1** (sin signo, la resta pide prestado).

### B.4 Mini-tarea 4 — Ejecutar paso a paso en gdb (2026-11-22)

**Ejemplo del Tutor** (los comandos):

```
gdb -q retos/fase-1/build/mt3
set disassembly-flavor intel
starti
display/i $rip
display $rax
display $rbx
display $eflags
si
```

**Respuesta final del estudiante** (su predicción, sobre `mt3` con `cmp rax, 14`, ya corregida):

| Tras | rax | rbx | ZF | Sigue |
|---|---|---|---|---|
| (arranque) | 0 | 0 | 0 | `mov rax, 20` |
| `mov rax, 20` | 20 | 0 | 0 | `mov rbx, 6` |
| `mov rbx, 6` | 20 | 6 | 0 | `sub rax, rbx` |
| `sub rax, rbx` | 14 | 6 | 0 | `cmp rax, 14` |
| `cmp rax, 14` | 14 | 6 | 1 | `je iguales` |
| `je iguales` | 14 | 6 | 1 | `mov rax, 60` bajo `iguales:` |

Los valores, la ZF tras `cmp` y el salto fueron correctos desde el principio. Correcciones: (1) `sub`
también escribe en la libreta; (2) en la máquina no hay «?», y al arrancar Linux deja los registros en 0;
(3) hay dos `mov rax, 60`, y el dedo va al de `iguales:`. gdb lo confirmó: el dedo saltó de `0x401011` a
`0x40101f`. Los corchetes de `$eflags` (`[ PF ZF IF ]`) son el soporte f⁻¹(1) de la libreta.

### B.5 Mini-tarea 5 — Bucle con indirección (2026-11-23)

**Concepto:** las piezas viven en `section .data`. `mov rsi, piezas` pone en la mesa el **número del
estante**; `[rsi]` trae la pieza; `inc rsi` avanza un estante. Es la sucesión a: {0,1,2,3} → bytes:
`rsi` recorre el dominio y `[rsi]` evalúa la función.

**Ejercicios previos de lectura** (con `piezas: db 5, 3, 8, 2`):

1. `mov rsi, piezas` / `inc rsi` / `inc rsi` / `mov al, [rsi]`. Respuesta final: `rsi = piezas + 2`,
   `al = 8`. Errores en el camino: primero omitió los `inc` (`al = 5`) y después se quedó un estante
   atrás (`al = 3`).
2. `mov rsi, piezas` / `add rsi, 3` / `mov al, [rsi]` / `dec rsi` / `mov al, [rsi]`. Primero sumó 3 a la
   **pieza** (5 + 3 = 8) en vez de al **estante**. Con la tabla de estantes reales (`0x402000` → 5, …),
   respuesta final correcta: `rsi = piezas + 3`, `al = 2`, `rsi = piezas + 2`, `al = 8`.

**Ejemplo del Tutor** (bucle **sin** indirección: suma 3 + 2 + 1, sale con 6):

```nasm
global _start
section .text
_start:
    mov  rcx, 3       ; contador
    mov  rdi, 0       ; acumulador
bucle:
    add  dil, cl      ; cl = byte bajo de rcx
    dec  rcx
    cmp  rcx, 0
    je   fin
    jmp  bucle
fin:
    mov  rax, 60
    syscall
```

**Respuesta final del estudiante** (solo, juntando bucle e indirección, `retos/fase-1/mt5.asm`):

```nasm
global _start
section .data
    piezas: db 5, 3, 8, 2

section .text
_start:
    mov rcx, 4          ; contador: 4 piezas
    mov rdi, 0          ; acumulador
    mov rsi, piezas     ; rsi apunta al primer estante

bucle:
    add dil, [rsi]      ; suma la pieza actual
    inc rsi             ; el dedo avanza al siguiente estante
    dec rcx
    cmp rcx, 0
    je fin
    jmp bucle

fin:
    mov rax, 60
    syscall             ; código de salida = rdi
```

- **Predicción:** 4 vueltas (5, 3, 8, 2); al salir `rcx = 0`, `rsi = piezas + 4`; código 5+3+8+2 = 18.
- **Verificación** (`trazar.sh --mem piezas`): `rdi` = 5 → 8 → 16 → 18; `rsi` = `0x402000` →
  `0x402004`; `je` salta en la 4.ª vuelta; `codigo: 18`. Todo coincide.
- **Pregunta final:** ¿qué vale ZF justo tras `dec rcx` en la 4.ª vuelta? Respuesta: **ZF = 1** (la
  traza lo marca `1*` en el paso 24). Matiz: no significa «son iguales», sino «la última cuenta dio 0».
  Por eso `cmp rcx, 0` sobra: `dec` ya dejó la marca.
- **Observaciones de la salida:** `rsi = 4202497` es `0x402001` en decimal. `[piezas] = 0x2c02080305` se
  lee de derecha a izquierda (`05 03 08 02`); el `2c` es el estante siguiente, que no es del arreglo. La
  máquina no sabe dónde termina un arreglo: semilla de los buffer overflows de Fase 2.

## Cierre

**Criterio de salida cumplido:** el estudiante lee un fragmento de Assembly x86 básico y traza, paso a paso, qué hace la CPU y cómo cambia el estado de los registros y de la memoria. Verificado en los trazados A.1 y A.2, el segundo de ellos con indirección.

**Reto de escritorio cumplido (2026-11-23):** escribió, ensambló y ejecutó Assembly x86-64 en WSL, y verificó en gdb y con `trazar.sh` cada predicción (Apéndice B). La transición de leer a escribir quedó hecha: el bucle con indirección de B.5 lo escribió solo, a partir de un ejemplo sin indirección.

**Gaps que pasan a la Fase 2:** la finitud (tamaños de tipos, overflow), las marcas SF y CF sin ejercicio propio, la distinción estante / pieza (dirección / contenido) que todavía tropezó en B.5, la intuición de que «el hardware se recupera solo» y la disciplina de predecir antes de correr.

La Fase 2 introduce C. Los conceptos cubiertos en este reporte —direcciones, indirección, stack, direcciones de retorno, organización de la memoria— son la materia prima directa de esa etapa: los punteros de C son exactamente los números-dirección de la Sección 8, y el primer contacto con buffer overflows es el desarrollo de la semilla sembrada en la Sección 7.4.
