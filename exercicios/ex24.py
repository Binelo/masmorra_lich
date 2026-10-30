# Exercício 24 - Arquivos
#
# Escreva uma lista de tarefas em um arquivo tarefas.txt (uma por linha)
# e depois leia o arquivo de volta e imprima numerado.
# Use with open(...). Pesquise a diferença entre os modos "w", "a" e "r".
# Dica: cuidado com acentos, use encoding="utf-8".


with open("tarefas.txt", "r", encoding="utf-8") as arquivo:
    for numero, linha in enumerate(arquivo, 1):
        print(f"{numero}. {linha.strip()}")