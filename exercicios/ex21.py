# Exercício 21 - Comprehensions
#
# Com dict comprehension, crie {palavra: tamanho} para uma lista de palavras.
#   ["python", "é", "legal"] -> {'python': 6, 'é': 1, 'legal': 5}

lista = ["python", "é", "legal"]

new_list = {x: len(x) for x in lista}

print(new_list)