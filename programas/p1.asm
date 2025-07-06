# Programa 1: Operações Aritméticas e Lógicas
# Demonstra o uso de li, add, sub, and, or, slt, slti:

li $t0, 15
li $t1, 10
add $t2, $t0, $t1     # $t2 = 25
sub $t3, $t0, $t1     # $t3 = 5
and $t4, $t0, $t1     # $t4 = 10
or  $t5, $t0, $t1     # $t5 = 15
slt $t6, $t1, $t0     # $t6 = 1 (10 < 15)
slti $t7, $t0, 20     # $t7 = 1 (15 < 20)
IMPRIMIR INTEIRO $t2
IMPRIMIR INTEIRO $t3
IMPRIMIR INTEIRO $t4
IMPRIMIR INTEIRO $t5
IMPRIMIR INTEIRO $t6
IMPRIMIR INTEIRO $t7
