# Exercício 22 - enumerate e zip
#
# 1) Use enumerate para imprimir uma lista numerada a partir de 1:
#    1. arroz
#    2. feijão
# 2) Use zip para juntar duas listas e imprimir:
#    nomes = ["Ana", "Bruno", "Carla"]
#    notas = [8.5, 6.0, 9.2]
#    -> Ana: 8.5 / Bruno: 6.0 / Carla: 9.2

compras = ["arroz", "feijão"]

for numero, item in enumerate(compras, 1):
    print(f"{numero}. {item}")


nomes = ["Ana", "Bruno", "Carla"]
notas = [8.5, 6.0, 9.2]

for nome, nota in zip(nomes, notas):
    print(f"{nome}: {nota}")