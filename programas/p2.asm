# Programa 2: Operações com Memória RISC-V
# Demonstra o uso de addi, sw, lw para manipulação de memória

addi x5, x0, 99       # x5 = 99
addi x6, x0, 123      # x6 = 123
addi x7, x0, 100      # x7 = 100 (endereço base)
sw x5, 0(x7)          # Armazena 99 na posição 100
sw x6, 4(x7)          # Armazena 123 na posição 104
lw x8, 0(x7)          # Carrega 99 em x8
lw x9, 4(x7)          # Carrega 123 em x9
addi x10, x8, 0       # a0 = x8 (99)
IMPRIMIR INTEIRO
addi x10, x9, 0       # a0 = x9 (123)
IMPRIMIR INTEIRO
