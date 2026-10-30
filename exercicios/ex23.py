# Exercício 23 - map e filter
#
# 1) Use map para converter ["1", "2", "3"] em [1, 2, 3].
# 2) Use filter para pegar só os números maiores que 10 de uma lista.
# 3) Reescreva os dois como list comprehension.
# Repare: map/filter devolvem um objeto "preguiçoso", precisa de list() para ver.

def funcao_map(n):
    return int(n)

lista_map = list(map(funcao_map, ["1", "2", "3"]))
print(lista_map)

lista_filter = list(filter(lambda n: n > 10, range(1, 20)))

print(lista_filter)



lista_map2 = [int(x) for x in ["1", "2", "3"]]
lista_filter2 = [x for x in range(1, 20) if x > 10]

print(lista_map2)
print(lista_filter2)