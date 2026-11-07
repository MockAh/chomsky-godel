El ciclo, en el taller

1. FETCH — buscar El carpintero mira dónde apunta su dedo (rip) y trae ese renglón. Casi siempre ya está en la repisa. Si no, viaje al almacén — y vuelve con 64 bytes. Lo que trae, lo sostiene en la mano (registro de instrucción).

2. DECODE — leer Mira el renglón y entiende dos cosas a la vez:

- qué verbo es (mov, cmp, jmp, je)
- cuánto mide ese renglón

La longitud viene implícita en el verbo. Por eso no hacen falta separadores en la hoja.

3. EXECUTE — hacer Ejecuta el verbo. Modifica un lugar:

- mov → una pieza en la mesa
- cmp → la libreta
- jmp / je → el dedo

4. AVANZAR Al dedo se le suma la longitud del renglón. Salvo que el verbo ya lo haya movido él mismo — ahí está el salto.

Y vuelve al 1.

Lo esencial: el carpintero no ve el programa. Ve un renglón, lo hace, mira el siguiente. Miles de millones de veces por segundo.
