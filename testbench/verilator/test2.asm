.section .text
.globl _start

_start:
    addi x1, x0, 1;
    addi x2, x0, 2;

    add x10, x1, x2;
    or x11, x1, x2;

    beq x10, x11, _loop;

    and x12, x2, x10;

    sw x10, 0(s1)

_loop:
    and x12, x1, x10;
