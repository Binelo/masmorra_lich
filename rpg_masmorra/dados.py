# ============================================================================
#  dados.py - lê os arquivos JSON da pasta dados/
# ============================================================================
#  Inimigos, itens e mapas ficam em arquivos JSON. Assim, para criar um
#  inimigo, item ou sala novos, você edita o JSON e não precisa mexer no código.
#  Os outros módulos importam daqui: dados.INIMIGOS, dados.ITENS, dados.ANDARES...
#
#  Os andares ficam em dados/andares.json (em ordem), e cada um aponta para
#  o mapa dele em dados/mapas/.
# ============================================================================

import json
import os

# Caminhos a partir da pasta deste arquivo, para funcionar de qualquer lugar
PASTA = os.path.dirname(os.path.abspath(__file__))
PASTA_DADOS = os.path.join(PASTA, "dados")


def carregar_json(nome_arquivo):
    caminho = os.path.join(PASTA_DADOS, nome_arquivo)
    with open(caminho, "r", encoding="utf-8") as arquivo:
        return json.load(arquivo)


INIMIGOS = carregar_json("inimigos.json")
ITENS = carregar_json("itens.json")
SAQUE = carregar_json("saque.json")

ANDARES = carregar_json("andares.json")                       # lista, na ordem do jogo
MAPAS = {andar["id"]: carregar_json(os.path.join("mapas", andar["mapa"]))
         for andar in ANDARES}                                # id do andar -> mapa
PRIMEIRO_ANDAR = ANDARES[0]["id"]


def info_andar(andar_id):
    return next(andar for andar in ANDARES if andar["id"] == andar_id)


def proximo_andar(andar_id):
    """Id do andar seguinte, ou None se este for o último."""
    ids = [andar["id"] for andar in ANDARES]
    posicao = ids.index(andar_id)
    return ids[posicao + 1] if posicao + 1 < len(ids) else None
