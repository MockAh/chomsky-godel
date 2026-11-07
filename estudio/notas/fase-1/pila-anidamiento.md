Tres respuestas, tres calibraciones distintas.

1 — Portapapeles. Buen instinto por el orden, pero es distinto: el portapapeles solo guarda uno. No hay pila, hay reemplazo. Lo último en entrar es lo único que hay.

1.1 — La libreta / flags. No. Los flags se sobrescriben en cada operación: no se apilan. Tampoco hay pila ahí.

1.2 — Orden lineal con primer elemento. Correcto formalmente. Pero lo importante es qué lo genera, y ahí está la respuesta que busco.

Es el anidamiento.

Piensa en cualquier proceso donde para terminar A tienes que suspenderlo, hacer B, y volver exactamente donde dejaste A. Si B a su vez suspende para hacer C, entonces C debe terminar antes que B, y B antes que A. El orden de retorno es forzosamente el inverso del orden de entrada.

Lo has visto mil veces:

- Paréntesis anidados. ((a+b)·(c+d)) — el último que abres es el primero que cierras. Es una gramática libre de contexto, y su reconocimiento requiere una pila. Esa es la definición misma de autómata de pila.
- Demostraciones con lemas. Suspendes el teorema, pruebas el lema, vuelves. Si el lema necesita otro lema, se anida.
- Recursión.

En la CPU: llamar a una función. El programa suspende lo que hacía, salta a otro lado, y tiene que volver exactamente al renglón siguiente. Si esa función llama a otra, se anida. El stack guarda las direcciones de retorno.

El carpintero: deja la hoja actual boca abajo sobre una pila, toma la nueva, trabaja, y al terminar destapa la de encima — que es forzosamente la última que dejó. No podría ser otra.

Y aquí está lo que vas a explotar en Fase 2. Esa dirección de retorno está guardada en memoria, en el stack, mezclada con datos que el programa escribe libremente.

Pregunta: ¿qué pasa si un dato mal medido se escribe más allá de su sitio y encima de la dirección de retorno?
