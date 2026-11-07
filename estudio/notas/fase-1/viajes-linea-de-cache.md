El viaje al almacén

El carpintero pide un renglón. Y sale de la bodega un tramo entero de la hoja: 64 bytes contiguos — el renglón pedido y sus vecinos, quiera o no.

Por qué: lo caro es ir, no cargar. El trayecto cuesta lo mismo con uno o con sesenta y cuatro. Si ya caminaste hasta allá, llénate los brazos.

Ese paquete de 64 bytes se llama línea de caché, y se queda en la repisa.

Dos mecanismos distintos, no confundirlos:

1. Traer vecinos (línea de caché) Pasa siempre que hay un viaje. Es automático y ciego: agarra el bloque completo. No es predicción — es que el bloque es la unidad mínima de transporte.

2. Adelantarse (prefetch) El carpintero nota que va leyendo la hoja en orden y manda traer los siguientes tramos antes de necesitarlos. Esto sí es predicción, y puede fallar.

El efecto conjunto: un bucle de 10 renglones se trae una vez, se queda en la repisa, y el carpintero lo lee millones de veces sin volver a caminar.

Por eso funciona todo: no hay un viaje por renglón. Hay un viaje por tramo, y casi todos los renglones ya estaban ahí.
