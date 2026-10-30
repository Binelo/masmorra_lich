import random

COMBINACOES = [
        (0, 1, 2), (0, 3, 6), (0, 4, 8), (1, 4, 7),
        (2, 5, 8), (2, 4, 6), (3, 4, 5), (6, 7, 8)
    ]
def desenhar_velha(posicoes):
    print(f'{posicoes[0]} {posicoes[1]} {posicoes[2]}')
    print(f'{posicoes[3]} {posicoes[4]} {posicoes[5]}')
    print(f'{posicoes[6]} {posicoes[7]} {posicoes[8]}')

def verificar_resultado(posicoes):
    for a, b, c in COMBINACOES:
        if posicoes[a] == posicoes[b] == posicoes[c] != "-":
            return True
    return None



def pegar_espaco_livre(posicoes):
    livres = [i for i, valor in enumerate(posicoes) if valor == "-"]

    return random.choice(livres)

# pego todas as que estão livres e comparo com as combinações para ver se colocando ali eu ganho
# se não ganhar faço o mesmo só que jogando com o inimigo
# se nenhum dos dois ganhar, jogo aleatorio
def jogada_pc(posicoes):
    livres = [i for i, valor in enumerate(posicoes) if valor == "-"]

    # 1. consigo ganhar?
    for i in livres:
        posicoes[i] = "O"
        ganhou = verificar_resultado(posicoes)
        posicoes[i] = "-"          # desfaz a simulação
        if ganhou:
            return i

    # 2. o jogador vai ganhar? então bloqueio
    for i in livres:
        posicoes[i] = "X"
        perderia = verificar_resultado(posicoes)
        posicoes[i] = "-"
        if perderia:
            return i

    # 3. nenhum dos dois: aleatório
    return random.choice(livres)


        
def ler_jogada(posicao):
    while True:
        try:
            jogada = int(input("Digite uma posição de 1 a 9: "))
        except ValueError:
            print("Digite um número.")
            continue

        if 1 <= jogada <= 9:
            if posicao[jogada - 1] != "-":
                print("posição já ocupada")
                continue
            else:
                return jogada
        print("A posição deve ser de 1 a 9.")
            


def jogar2p():
    posicoes = ["-", "-", "-", "-", "-", "-", "-", "-", "-"]

    while True:
        jogada_a = ler_jogada(posicoes)
        if posicoes[jogada_a - 1] == "-":
            posicoes[jogada_a - 1] = "X"
        desenhar_velha(posicoes)
        if verificar_resultado(posicoes):
            print("X ganhou!")
            break
        if "-" not in posicoes:
            print("Deu velha!")
            break

        jogada_b = ler_jogada(posicoes)
        if posicoes[jogada_b - 1] == "-":
            posicoes[jogada_b - 1] = "O"
        desenhar_velha(posicoes)
        if verificar_resultado(posicoes):
            print("O ganhou!")
            break
        if "-" not in posicoes:
            print("Deu velha!")
            break


def jogar_pc():
    posicoes = ["-", "-", "-", "-", "-", "-", "-", "-", "-"]

    while True:
        jogada_a = ler_jogada(posicoes)
        if posicoes[jogada_a - 1] == "-":
            posicoes[jogada_a - 1] = "X"
        desenhar_velha(posicoes)
        if verificar_resultado(posicoes):
            print("X ganhou!")
            break
        if "-" not in posicoes:
            print("Deu velha!")
            break

        print("-------------")
        posicoes[pegar_espaco_livre(posicoes)] = "O"
        desenhar_velha(posicoes)
        if verificar_resultado(posicoes):
            print("O ganhou!")
            break
        if "-" not in posicoes:
            print("Deu velha!")
            break

def jogar_pc_esperto():
    posicoes = ["-", "-", "-", "-", "-", "-", "-", "-", "-"]

    while True:
        jogada_a = ler_jogada(posicoes)
        if posicoes[jogada_a - 1] == "-":
            posicoes[jogada_a - 1] = "X"
        desenhar_velha(posicoes)
        if verificar_resultado(posicoes):
            print("X ganhou!")
            break
        if "-" not in posicoes:
            print("Deu velha!")
            break

        print("-------------")
        posicoes[jogada_pc(posicoes)] = "O"
        desenhar_velha(posicoes)
        if verificar_resultado(posicoes):
            print("O ganhou!")
            break
        if "-" not in posicoes:
            print("Deu velha!")
            break




jogar_pc_esperto()