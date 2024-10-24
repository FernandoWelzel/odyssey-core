.section .text
.globl _start

_start:
    addi x1, x0, 1; # t1 = t1 + 1
    addi x2, x0, 2; # t2 = t1 + 2
    addi x3, x0, 3; # t3 = t1 + 3
    addi x4, x0, 4; # t4 = t1 + 4
    addi x5, x0, 5; # t5 = t1 + 5
    addi x6, x0, 6; # t6 = t1 + 6
    addi x7, x0, 7; # t7 = t1 + 7
    addi x8, x0, 8; # t8 = t1 + 8
    addi x9, x0, 9; # t9 = t1 + 9

    addi x10, x0, 9; # t9 = t1 + 9

    add x10, x1, x2; # x10 = x1 + x2

    sw x10, 0(s1)
    