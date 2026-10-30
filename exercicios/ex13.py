# Exercício 13 - Dicionários
#
# Conte a frequência de cada palavra de um texto usando um dict.
# Depois refaça usando collections.Counter.
#
# Exemplo: "o gato e o rato e o cão"
#   -> {'o': 3, 'gato': 1, 'e': 2, 'rato': 1, 'cão': 1}
# Lembre dos casos de borda: maiúsculas e pontuação.

# frase = input("Escreva uma frase: ")

from collections import Counter

frase = "o gato e o rato e o cão"

palavras = frase.lower().split()
dicio = {}
for palavra in palavras:
    if palavra in dicio:
        dicio[palavra] = dicio[palavra] + 1
    else:
        dicio[palavra] = 1

print(dicio)

c = Counter(palavras)
print(c)