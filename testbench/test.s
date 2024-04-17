.section .text
.globl _start

_start:
    add a0, a0, a1
    add t0, t0, a1
    sub a0, a0, a1
    sub t0, t0, a1
    xor a0, a0, a1
    xor a0, a0, a1
