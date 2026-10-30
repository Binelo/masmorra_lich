# ============================================================================
#  mapa.py - salas, descrição e movimentação
# ============================================================================
#  Cada andar tem um mapa em dados/mapas/<andar>.json. Campos que uma sala pode ter:
#    "nome", "descricao", "saidas"   - obrigatórios
#    "inimigo": "goblin"             - chave de um inimigo do inimigos.json
#    "itens": ["chave"]               - itens FIXOS no chão (chaves do itens.json)
#
#  No topo do arquivo do mapa, "itens_espalhados" coloca um item numa sala sorteada:
#    {"item": "chave", "salas": ["arsenal", "cripta", ...]}
#    "saque": [{"tabela": "armas", "chance": 0.5}]
#                                     - itens SORTEADOS ao criar o mapa (tabelas no saque.json)
#    "mercador": {"pocao": 10}       - itens à venda e preços
#    "fonte": true                   - o comando "beber" restaura vida e energia
#    "trancada": "chave"             - item necessário para entrar
#    "npc": {"nome": "...", "falas": ["...", "..."]}   - alguém para conversar (comando "falar")
#    "bau": {"tabela": "armas", "chance_mimico": 0.35}
#                                     - um baú (comando "abrir"); pode ser um mímico
#    "texto_trancada": "..."         - mensagem quando a porta está trancada
# ============================================================================

import copy
import random
from collections import Counter

import dados
from itens import nome_item, sortear_item

def sala_inicial(andar):
    return dados.MAPAS[andar]["inicio"]

DIRECOES = {"n": "norte", "s": "sul", "l": "leste", "o": "oeste",
            "norte": "norte", "sul": "sul", "leste": "leste", "oeste": "oeste"}


def criar_mapa(heroi=None, andar=dados.PRIMEIRO_ANDAR):
    # deepcopy cria uma cópia COMPLETA (incluindo os dicts de dentro).
    # Sem isso, cada jogo novo alteraria o mesmo dicionário carregado do JSON:
    # um monstro derrotado continuaria "derrotado" no próximo jogo.
    mapa = copy.deepcopy(dados.MAPAS[andar]["salas"])

    # Sorteia o saque de cada sala. O resultado vira itens normais,
    # então o save guarda exatamente o que saiu (não sorteia de novo ao carregar).
    sorteados = set()
    for sala in mapa.values():
        for sorteio in sala.pop("saque", []):
            if random.random() < sorteio["chance"]:
                item = sortear_item(sorteio["tabela"], heroi, sorteados)
                if item:
                    sala["itens"].append(item)
                    sorteados.add(item)

    # Baús: decide agora se cada um é um mímico e o que tem dentro
    for sala in mapa.values():
        if "bau" in sala:
            config = sala["bau"]
            item = sortear_item(config["tabela"], heroi, sorteados)
            if item:
                sorteados.add(item)
            sala["bau"] = {"mimico": random.random() < config.get("chance_mimico", 0),
                           "itens": [item] if item else []}

    # Itens espalhados: cada um vai para UMA sala sorteada da lista (ex.: a chave)
    for espalhado in dados.MAPAS[andar].get("itens_espalhados", []):
        sala_sorteada = random.choice(espalhado["salas"])
        mapa[sala_sorteada]["itens"].append(espalhado["item"])
    return mapa


def texto_da_sala(sala):
    """A descrição muda com o que já aconteceu na sala:
    - "descricao":       com o inimigo lá (como você a encontra)
    - "descricao_vazia": depois que o inimigo foi derrotado (ou se nunca esteve lá)
    - "descricao_seca":  depois de beber da fonte (o "fonte" vira False)"""
    if sala.get("inimigo"):
        return sala["descricao"]
    if sala.get("fonte") is False and sala.get("descricao_seca"):
        return sala["descricao_seca"]
    return sala.get("descricao_vazia", sala["descricao"])


def descrever_sala(sala):
    print(f"\n=== {sala['nome']} ===")
    print(texto_da_sala(sala))
    if sala["itens"]:
        # Counter conta repetidos: ["pocao", "pocao", "eter"] -> {"pocao": 2, "eter": 1}
        contagem = Counter(sala["itens"])
        nomes = ", ".join(nome_item(c) + (f" x{q}" if q > 1 else "") for c, q in contagem.items())
        print(f"Você vê no chão: {nomes}.")
    if sala.get("vitima_do_lich"):
        print(f"Os restos de {sala['vitima_do_lich']} estão espalhados pelo chão, secos, "
              f"como se a vida tivesse sido sugada.")
    if sala.get("npc"):
        extras = ", comprar, vender" if sala.get("mercador") else ""
        print(f"{sala['npc']['nome']} está aqui. (falar{extras})")
    if sala.get("bau"):
        print("Há um baú de ferro reforçado aqui. (abrir)")
    print(f"Saídas: {', '.join(sala['saidas'])}")


def mostrar_mapa(sala, andar):
    print(f"\n  {dados.info_andar(andar)['nome']}\n")
    print("\n".join(dados.MAPAS[andar]["desenho"]) + "\n")
    print(f"  Você está em: {sala['nome']}")


def tentar_andar(heroi, mapa, sala_atual, direcao):
    """Retorna o id da próxima sala, ou None se não der pra ir."""
    saidas = mapa[sala_atual]["saidas"]
    if direcao not in saidas:
        print("  Não há passagem nessa direção.")
        return None

    destino = saidas[direcao]
    item_necessario = mapa[destino].get("trancada")
    if item_necessario:
        if item_necessario is True:            # saves da versão antiga usavam True
            item_necessario = "chave"
        if heroi.inventario.get(item_necessario, 0) > 0:
            print(f"  Você usa: {nome_item(item_necessario)}. A porta range e se abre...")
            heroi.inventario[item_necessario] -= 1
            mapa[destino]["trancada"] = False
        else:
            print("  " + mapa[destino].get("texto_trancada", "A porta está trancada."))
            return None
    return destino
