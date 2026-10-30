# Exercício 12 - Listas
#
# Remova as duplicatas de uma lista mantendo a ordem original.
#
# Exemplo: [3, 1, 3, 2, 1, 5] -> [3, 1, 2, 5]
# Desafio: pense por que set(lista) sozinho não resolve.

lista = [3, 1, 3, 2, 1, 5]
i = 0
copia_lista = []
while i < len(lista):
    if lista[i] not in copia_lista:
        copia_lista.append(lista[i])
    i+=1
print(copia_lista)