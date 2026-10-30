# Exercício 20 - Comprehensions
#
# Com list comprehension, gere os quadrados dos números PARES de 1 a 20.
#   -> [4, 16, 36, 64, 100, 144, 196, 256, 324, 400]
# Faça primeiro com for normal e depois em uma linha.

lista = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20]
new_list = []
for item in lista:
    if item % 2 == 0:
        new_list.append(item ** 2)

print(new_list)

newer_list = [x ** 2 for x in lista if x % 2 == 0]

print(newer_list)