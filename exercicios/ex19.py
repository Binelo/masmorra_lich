# Exercício 19 - Funções
#
# Faça o fatorial de duas formas: recursiva e iterativa (com loop).
#   fatorial(5) -> 120   (5 * 4 * 3 * 2 * 1)
#   fatorial(0) -> 1
# O que acontece se chamar a recursiva com um número negativo? Trate isso.

def fat_recursiva(n):
    valor = n
    if n > 1 :
        valor = n * fat_recursiva(n - 1)
    return valor
print(fat_recursiva(5))

def fat_iterativa(n):
    valor = 1 if n == 0 else n
    while n > 1:
        valor = valor * (n - 1)
        n-=1
    return valor

print(fat_iterativa(5))