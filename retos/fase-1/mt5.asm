global _start
section .data
    piezas: db 5, 3, 8, 2

section .text
_start:
    mov rcx, 4          ; contador: 4 piezas
    mov rdi, 0          ; acumulador: empezamos en 0
    mov rsi, piezas     ; rsi apunta al primer estante (la primera pieza)

bucle:
    add dil, [rsi]      ; suma el byte actual al acumulador (dil)
    inc rsi             ; el dedo avanza al siguiente estante
    dec rcx             ; decrementamos el contador
    cmp rcx, 0          ; ¿llegamos a cero?
    je fin              ; si es cero, salta a fin
    jmp bucle           ; si no, vuelve a empezar el bucle

fin:
    mov rax, 60         ; syscall para exit
    syscall             ; el código de salida será lo que haya en rdi (18)