# Programa 1: Operações Aritméticas e Lógicas RISC-V
# Demonstra o uso de addi, add, sub, and, or, slt, slti:

addi x5, x0, 15       # x5 = 15
addi x6, x0, 10       # x6 = 10
add x7, x5, x6        # x7 = 25
sub x8, x5, x6        # x8 = 5
and x9, x5, x6        # x9 = 10
or x10, x5, x6        # x10 = 15
slt x11, x6, x5       # x11 = 1 (10 < 15)
slti x12, x5, 20      # x12 = 1 (15 < 20)
addi x10, x0, 25      # a0 = 25 para imprimir
IMPRIMIR INTEIRO
addi x10, x0, 5       # a0 = 5
IMPRIMIR INTEIRO
addi x10, x0, 10      # a0 = 10
IMPRIMIR INTEIRO
addi x10, x0, 15      # a0 = 15
IMPRIMIR INTEIRO
addi x10, x0, 1       # a0 = 1
IMPRIMIR INTEIRO
addi x10, x0, 1       # a0 = 1
IMPRIMIR INTEIRO
