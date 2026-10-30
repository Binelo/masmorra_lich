# Exercício 11 - Listas
#
# Dada uma lista de números, ache o maior, o menor e a média
# SEM usar max(), min() e sum(). Depois refaça usando eles.
#
# Exemplo: numeros = [7, 2, 9, 4, 10, 1]
#   maior: 10 | menor: 1 | média: 5.5

def estatisticas_manual(numeros):
    if not numeros:          # lista vazia é "falsa" em Python
        return None

    maior = menor = numeros[0]
    soma = 0

    for n in numeros:
        soma += n
        if n > maior:
            maior = n
        if n < menor:
            menor = n

    return maior, menor, soma / len(numeros)


def estatisticas(numeros):
    if not numeros:
        return None
    return max(numeros), min(numeros), sum(numeros) / len(numeros)


numeros = [7, 2, 9, 4, 10, 1]

maior, menor, media = estatisticas_manual(numeros)
print(f"Maior: {maior} | Menor: {menor} | Média: {media:.2f}")

print(estatisticas(numeros))   # (10, 1, 5.5)