# ============================================================================
#  A MASMORRA DO LICH - um RPG de texto no terminal
# ============================================================================
#  Para jogar:  py main.py   (ou python main.py)
#
#  Organização:
#    main.py         menu inicial (este arquivo)
#    jogo.py         exploração e comandos
#    batalha.py      combate por turnos
#    personagens.py  classes de heróis e inimigos
#    itens.py        itens, inventário e loja
#    mapa.py         salas e movimentação
#    save.py         salvar/carregar (só para pausar: a morte é permanente)
#    progresso.py    Ecos e o Santuário (o que sobrevive entre as partidas)
#    caido.py        os heróis caídos e os Liches que nascem deles
#    dados.py        lê os JSON da pasta dados/
#    simular.py      simulações para testar o balanceamento
#    dados/*.json    inimigos, itens, saque e andares (edite aqui para criar conteúdo)
#    dados/mapas/    um mapa por andar
# ============================================================================

import json

import jogo
import progresso
import save
import dados

TITULO = r"""
  ================================================
       A   M A S M O R R A   D O   L I C H
  ================================================
"""


def novo_jogo():
    heroi = jogo.criar_personagem()
    progresso.aplicar_melhorias(heroi)          # o que você comprou no Santuário
    print(f"\n{heroi.nome}, o {type(heroi).__name__}, começa sua descida. "
          "Digite 'ajuda' para ver os comandos.")
    return heroi, jogo.jogar_campanha(heroi, dados.PRIMEIRO_ANDAR)


def continuar_jogo():
    """Carrega a partida pausada. O save é consumido: se você sair sem salvar
    de novo (ou morrer), ela não volta."""
    try:
        heroi, andar, sala, mapa = save.carregar()
    except (json.JSONDecodeError, KeyError, OSError):
        print("  Não foi possível carregar o save.")
        save.apagar()
        return None, None
    save.apagar()
    print(f"\n  Bem-vindo de volta, {heroi.nome}! ({dados.info_andar(andar)['nome']})")
    return heroi, jogo.jogar_campanha(heroi, andar, sala, mapa)


def menu():
    """Mostra as opções e devolve a escolha."""
    ecos = progresso.carregar()["ecos"]
    print()
    opcoes = {}
    if save.existe_save():
        print("  1 - Continuar a partida pausada")
        opcoes["1"] = "continuar"
        print("  2 - Novo jogo (a partida pausada será perdida)")
        opcoes["2"] = "novo"
    else:
        print("  1 - Novo jogo")
        opcoes["1"] = "novo"
    print(f"  3 - Santuário ({ecos} Ecos)")
    opcoes["3"] = "santuario"
    print("  0 - Sair")
    opcoes["0"] = "sair"

    while True:
        escolha = input("> ").strip()
        if escolha in opcoes:
            return opcoes[escolha]
        print("  Opção inválida.")


def main():
    print(TITULO)
    while True:                                 # o jogo só fecha quando o jogador escolhe sair
        escolha = menu()
        if escolha == "sair":
            print("  Até a próxima!")
            return
        if escolha == "santuario":
            progresso.santuario()
            continue
        if escolha == "novo":
            save.apagar()                       # começar de novo descarta a partida pausada
            heroi, resultado = novo_jogo()
        else:
            heroi, resultado = continuar_jogo()
        if resultado in ("morreu", "venceu", "abandonou"):
            save.apagar()                       # morte permanente: nada de voltar no tempo
            progresso.fim_de_partida(heroi, resultado)


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print("\n  Até a próxima!")
