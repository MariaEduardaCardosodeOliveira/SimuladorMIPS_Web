# Programa 3: SLT/SLTI + Fluxo Simples RISC-V
# Demonstra o uso de addi, add, slt, slti e ecall

addi x5, x0, 7        # x5 = 7
addi x6, x0, 5        # x6 = 5
add x7, x5, x6        # x7 = 12
slt x8, x5, x6        # x8 = 0 (7 < 5 é falso)
slt x9, x6, x5        # x9 = 1 (5 < 7 é verdadeiro)
slti x10, x7, 20      # x10 = 1 (12 < 20 é verdadeiro)
slti x11, x7, 10      # x11 = 0 (12 < 10 é falso)
addi x10, x0, 12      # a0 = 12
IMPRIMIR INTEIRO
addi x10, x0, 0       # a0 = 0
IMPRIMIR INTEIRO
addi x10, x0, 1       # a0 = 1
IMPRIMIR INTEIRO
addi x10, x0, 1       # a0 = 1
IMPRIMIR INTEIRO
addi x10, x0, 0       # a0 = 0
IMPRIMIR INTEIRO
