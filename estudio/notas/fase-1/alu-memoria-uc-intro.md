Bienvenido. Cierre de Fase 0 leído: tienes la base sólida — booleana, palabra, atomicidad, complemento a dos, direccionamiento por byte. La ALU quedó como caja negra: un sumador binario sobre palabras. Hoy la abrimos, y con ella toda la CPU.

Cápsula 1 — La CPU como conjunto finito nombrado

Concepto. Una CPU es un puñado pequeño de unidades coordinadas por un reloj. Las tres centrales:

- ALU — ejecuta operaciones aritméticas y booleanas sobre palabras.
- Registros — memoria interna ultra-rápida, en cantidad fija y minúscula (en x86-64, 16 de propósito general).
- Unidad de control — decide qué hacer en cada ciclo leyendo la siguiente instrucción desde memoria.

Conexión. En Fase 0 las palabras y operaciones vivían en abstracto. Aquí cada palabra ocupa físicamente un registro nombrado (rax, rbx, …) y la ALU opera estrictamente sobre operandos sacados de esos registros. El espacio de trabajo del procesador es finito, nombrado y pequeño — la antítesis de la cinta infinita de Turing. Esa cinta no desaparece: se reencarna como RAM, pero el cómputo real ocurre solo cuando el dato está en un registro.

Pregunta. Si la ALU es binaria (dos operandos → un resultado) y los registros de propósito general son ~16, en una palabra:

¿Qué predicción haces sobre lo que va a pasar cuando un programa tenga, digamos, 200 variables vivas al mismo tiempo? ¿De dónde tiene que salir y entrar el dato?

---
Buenas preguntas — la intuición de 1.1 es la correcta y es estructural. Por partes:

Sobre las instrucciones (1 y 1.1):

Las instrucciones viven en memoria, junto a los datos. Esto es la arquitectura de von Neumann: programa y datos comparten el mismo espacio direccionable. La Unidad de Control no las guarda — las lee una a una desde la dirección que apunta el Instruction Pointer (rip en x86-64).

¿Y cómo opera la UC si no tiene instrucciones propias? Aquí el punto duro: la UC no es programable, es circuito. Es un autómata finito materializado con compuertas — exactamente las de Fase 0. Su "comportamiento" no son instrucciones almacenadas: es una red de NANDs grabada en silicio que, ante un patrón de bits (la instrucción leída), activa unas líneas de control u otras. Reprogramar la UC sería rediseñar el chip.

Conexión formal: la UC es la función de transición δ de la Máquina de Turing, hecha hardware. Las instrucciones en memoria son el contenido de la cinta. La universalidad se logra cambiando lo que hay en la cinta, no la UC.

Sobre los registros (1.2):

- En x86-64, los registros de propósito general enteros son 16: rax, rbx, rcx, rdx, rsi, rdi, rbp, rsp, r8…r15. Cada uno mide exactamente 1 palabra = 64 bits = 8 bytes.
- Sí, palabra varía con la arquitectura: x86-32 tenía 8 GP de 32 bits (eax, ebx…); ARMv8 tiene 31 GP de 64 bits; un microcontrolador AVR tiene 32 GP de 1 byte. Ancho de palabra = ancho de GP = ancho de las direcciones nativas. Las tres cosas se mueven juntas por diseño.
- Hay además registros que no son GP y no entran en esa cuenta: el instruction pointer rip, el flags register rflags (donde la ALU deposita zero/carry/sign/overflow tras cada operación), los SIMD/FP (xmm0…xmm15, 128 bits para vectorización), registros de control privilegiados (cr0, cr3…), segmentos, etc. Cuando dije "16" me refería al pool donde se hace el trabajo aritmético cotidiano sobre enteros.

Retomando la pregunta original, ahora con los números concretos: 16 GP × 8 bytes = 128 bytes de espacio de trabajo verdaderamente "en mente" de la CPU.

Un programa con 200 variables enteras vivas a la vez tiene que… ¿qué? ¿De dónde sale cada dato cuando la ALU lo necesita y a dónde vuelve cuando termina con él?
