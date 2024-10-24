
main.elf:     file format elf32-littleriscv


Disassembly of section .text:

00000000 <main>:
   0:	fe010113          	addi	sp,sp,-32
   4:	00812e23          	sw	s0,28(sp)
   8:	02010413          	addi	s0,sp,32
   c:	fe042623          	sw	zero,-20(s0)
  10:	00000793          	li	a5,0
  14:	00078513          	mv	a0,a5
  18:	01c12403          	lw	s0,28(sp)
  1c:	02010113          	addi	sp,sp,32
  20:	00008067          	ret
