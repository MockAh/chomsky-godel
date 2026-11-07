# Plan general de aprendizaje: Ingeniería en Sistemas y Ciberseguridad

> Fuente: `Prompt_Maestro_2_Plan General de Aprendizaje`. Brújula permanente: dónde estamos, de dónde
> venimos y hacia dónde vamos. **Nunca propongas atajos ni saltes fases**: cada una es prerequisito
> estructural de la siguiente.

| Fase | Tema | Contenido | Criterio de salida |
|---|---|---|---|
| 0 | **El puente:** de la matemática a la lógica de la máquina | Álgebra booleana y compuertas. Representación de datos: bits, bytes, hex, ASCII, Unicode. Cómo un transistor se convierte en lógica. | Razona en binario y hexadecimal con fluidez, y entiende cómo la lógica booleana materializa las operaciones matemáticas. |
| 1 | **La máquina desnuda:** arquitectura | CPU: ALU, registros, ciclo fetch-decode-execute. Memoria: RAM, stack, heap, caché. Assembly x86 básico. | Lee Assembly básico y traza mentalmente qué hace una CPU instrucción por instrucción. |
| 2 | **El lenguaje del sistema:** C | Punteros, memoria manual, structs. Cómo C se convierte en Assembly. Primer contacto real con buffer overflows. | Escribe programas pequeños en C que manipulan memoria manualmente, y entiende qué ocurre debajo. |
| 3 | **El sistema operativo:** quién controla la máquina | Procesos, hilos, scheduling. Sistema de archivos y permisos. Linux desde adentro: syscalls, kernel space vs user space. | Explica qué ocurre a nivel de OS cuando ejecuta un programa, y navega Linux con soltura técnica. |
| 4 | **Las redes:** cómo las máquinas se hablan | Modelo OSI y TCP/IP. DNS, HTTP, TLS. Análisis de tráfico real con Wireshark. | Lee una captura de red y entiende qué ocurre en cada capa. |
| 5 | **Fundamentos de Ciberseguridad** | Criptografía aplicada. Autenticación, autorización, PKI. Primer CTF real. | Resuelve al menos un CTF básico de forma autónoma. |
| 6 | **Bifurcación:** ofensivo o defensivo | Ofensivo: pentesting, exploits, Metasploit, ingeniería inversa. Defensivo: SIEM, forense, threat hunting, blue team. | Sin fin fijo: es el inicio de una especialización. |

**Lógica pedagógica del orden:** sigue la cadena causal real de cómo funciona una computadora, del
transistor al exploit. Saltarse una fase es como estudiar Topología sin Teoría de Conjuntos: técnicamente
posible, pero estructuralmente costoso.
