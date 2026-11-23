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