# Exercício 25 - Exceções
#
# Crie uma função ler_inteiro(mensagem) que pede um número ao usuário
# e repete até ele digitar um inteiro válido, tratando ValueError.
# Depois reaproveite essa função para reescrever o ex2 ou ex4.
# (É aquele while True / try / except que você já repetiu várias vezes.)

def ler_inteiro(mensagem):
    while True:
        try:
            n = int(input("Digite um número: "))
            break
        except ValueError:
            print("Apenas números inteiros são aceitos.")
    return n

