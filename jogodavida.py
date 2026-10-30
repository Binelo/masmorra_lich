# Jogo da Vida de Conway
#
# Regras (aplicadas em todas as células ao mesmo tempo, a cada geração):
#   1. Viva com 2 ou 3 vizinhos vivos  -> continua viva
#   2. Viva com menos de 2 vizinhos     -> morre (solidão)
#   3. Viva com mais de 3 vizinhos      -> morre (superpopulação)
#   4. Morta com exatamente 3 vizinhos  -> nasce
#
# Para parar a animação: Ctrl + C

import os
import random
import time

LINHAS = 20
COLUNAS = 40
VELOCIDADE = 0.15   # segundos entre uma geração e outra

VIVA = 1
MORTA = 0


# ---------------------------------------------------------------------------
# Criar a grade
# ---------------------------------------------------------------------------

def criar_grade_vazia():
    # Comprehension: cada volta cria uma linha NOVA (nunca use [[0] * C] * L)
    return [[MORTA] * COLUNAS for _ in range(LINHAS)]


def criar_grade_aleatoria(chance_de_viver=0.05):
    # random.random() devolve um número entre 0 e 1.
    # Se ele for menor que 0.25, a célula nasce viva (25% de chance).
    return [
        [VIVA if random.random() < chance_de_viver else MORTA for _ in range(COLUNAS)]
        for _ in range(LINHAS)
    ]


def colocar_padrao(grade, padrao, linha_inicial, coluna_inicial):
    # Um padrão é uma lista de posições (linha, coluna) relativas ao canto dele.
    # Somamos a posição inicial pra "carimbar" o desenho em qualquer lugar.
    for l, c in padrao:
        grade[linha_inicial + l][coluna_inicial + c] = VIVA


# Alguns padrões famosos, como listas de tuplas (linha, coluna)
BLINKER = [(0, 0), (0, 1), (0, 2)]                     # pisca: horizontal <-> vertical
GLIDER = [(0, 1), (1, 2), (2, 0), (2, 1), (2, 2)]      # anda na diagonal
NAVE = [(0, 0), (0, 3), (1, 4), (2, 0), (2, 4),        # "nave espacial leve":
        (3, 1), (3, 2), (3, 3), (3, 4)]                # anda pra direita


# ---------------------------------------------------------------------------
# Lógica do jogo
# ---------------------------------------------------------------------------

def contar_vizinhos(grade, l, c):
    total = 0
    # dl e dc vão de -1 a 1: as 9 posições em volta (incluindo a própria)
    for dl in (-1, 0, 1):
        for dc in (-1, 0, 1):
            if dl == 0 and dc == 0:
                continue                      # pula a própria célula
            nl = l + dl                       # linha do vizinho
            nc = c + dc                       # coluna do vizinho
            # Só olha se estiver dentro da grade (grade[-1] não dá erro,
            # pegaria a última linha e contaria errado)
            if 0 <= nl < LINHAS and 0 <= nc < COLUNAS:
                total += grade[nl][nc]        # viva = 1, morta = 0
    return total


def proxima_geracao(grade):
    # Não alteramos a grade atual enquanto lemos ela (mesma lição do ex12):
    # se mudássemos uma célula no meio, a vizinha dela contaria errado.
    # Então montamos uma grade NOVA e devolvemos ela.
    nova = criar_grade_vazia()

    for l in range(LINHAS):
        for c in range(COLUNAS):
            vizinhos = contar_vizinhos(grade, l, c)
            viva = grade[l][c] == VIVA

            if viva and vizinhos in (2, 3):
                nova[l][c] = VIVA             # regra 1: sobrevive
            elif not viva and vizinhos == 3:
                nova[l][c] = VIVA             # regra 4: nasce
            # qualquer outro caso: fica MORTA (regras 2 e 3),
            # e a grade nova já começa toda morta

    return nova


def contar_vivas(grade):
    # sum de uma linha soma os 1s; o sum de fora soma todas as linhas
    return sum(sum(linha) for linha in grade)


# ---------------------------------------------------------------------------
# Tela
# ---------------------------------------------------------------------------

def limpar_tela():
    # "nt" é o Windows; Linux e Mac usam "clear"
    os.system("cls" if os.name == "nt" else "clear")


def desenhar(grade, geracao):
    print(f"Geração {geracao} | células vivas: {contar_vivas(grade)} | Ctrl+C para sair")
    for linha in grade:
        print("".join("#" if celula == VIVA else "." for celula in linha))


# ---------------------------------------------------------------------------
# Programa principal
# ---------------------------------------------------------------------------

def escolher_grade_inicial():
    print("Jogo da Vida")
    print("1 - Aleatório")
    print("2 - Glider (anda na diagonal)")
    print("3 - Blinker (pisca)")
    print("4 - Nave + glider")

    while True:
        opcao = input("Escolha: ")
        if opcao in ("1", "2", "3", "4"):
            break
        print("Opção inválida.")

    if opcao == "1":
        return criar_grade_aleatoria()

    grade = criar_grade_vazia()
    if opcao == "2":
        colocar_padrao(grade, GLIDER, 1, 1)
    elif opcao == "3":
        colocar_padrao(grade, BLINKER, LINHAS // 2, COLUNAS // 2 - 1)
    else:
        colocar_padrao(grade, NAVE, 3, 2)
        colocar_padrao(grade, GLIDER, 10, 20)
    return grade


def main():
    grade = escolher_grade_inicial()
    geracao = 0

    try:
        while True:
            limpar_tela()
            desenhar(grade, geracao)

            if contar_vivas(grade) == 0:
                print("Todas as células morreram.")
                break

            grade = proxima_geracao(grade)
            geracao += 1
            time.sleep(VELOCIDADE)
    except KeyboardInterrupt:
        # Ctrl+C lança essa exceção; capturamos pra sair sem mostrar erro
        print("\nFim!")


if __name__ == "__main__":
    main()
