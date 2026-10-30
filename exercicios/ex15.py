# Exercício 15 - Ordenação
#
# Ordene uma lista de dicionários por idade usando
# sorted(..., key=lambda ...).
#
# pessoas = [
#     {"nome": "Ana", "idade": 30},
#     {"nome": "Bruno", "idade": 22},
#     {"nome": "Carla", "idade": 27},
# ]
# Extra: ordene também da mais velha para a mais nova (parâmetro reverse).

pessoas = [
    {"nome": "Ana", "idade": 30},
    {"nome": "Bruno", "idade": 22},
    {"nome": "Carla", "idade": 27},
]

pessoas_ordenadas = sorted(pessoas, key=lambda x: x["idade"])
print(pessoas_ordenadas)
