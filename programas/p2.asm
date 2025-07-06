# Programa 2: Operações com Memória
# Demonstra o uso de li, sw, lw para manipulação de memória

li $t0, 99
li $t1, 123
sw $t0, (100)        # Armazena 99 na posição 100
sw $t1, (104)        # Armazena 123 na posição 104
lw $t2, (100)        # Carrega 99 em $t2
lw $t3, (104)        # Carrega 123 em $t3
IMPRIMIR INTEIRO $t2
IMPRIMIR INTEIRO $t3
