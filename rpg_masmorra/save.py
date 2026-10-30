# ============================================================================
#  save.py - salvar e carregar o jogo em JSON
# ============================================================================

import json
import os

import dados
from itens import migrar_save_antigo
from personagens import CLASSES

ARQUIVO_SAVE = os.path.join(dados.PASTA, "save.json")


def existe_save():
    return os.path.exists(ARQUIVO_SAVE)


def apagar():
    """Morte permanente: o save não sobrevive à morte, e é consumido ao continuar."""
    if os.path.exists(ARQUIVO_SAVE):
        os.remove(ARQUIVO_SAVE)


def salvar(heroi, sala_atual, mapa, andar):
    estado = {
        "classe": type(heroi).__name__,   # "Guerreiro", "Mago" ou "Ladino"
        # vars() devolve os atributos do objeto como dict; funções não vão pro JSON
        "heroi": {nome: valor for nome, valor in vars(heroi).items() if not callable(valor)},
        "andar": andar,
        "sala": sala_atual,
        "mapa": mapa,
    }
    with open(ARQUIVO_SAVE, "w", encoding="utf-8") as arquivo:
        json.dump(estado, arquivo, indent=2, ensure_ascii=False)
    print("  Jogo salvo!")


def carregar():
    """Retorna (heroi, andar, sala, mapa). Pode lançar json.JSONDecodeError ou KeyError.
    Não apaga o arquivo: quem chama decide (o main apaga depois de carregar com sucesso)."""
    with open(ARQUIVO_SAVE, "r", encoding="utf-8") as arquivo:
        estado = json.load(arquivo)
    classe = CLASSES[estado["classe"]]           # texto -> classe de verdade
    heroi = classe(estado["heroi"]["nome"])      # cria o herói...
    vars(heroi).update(estado["heroi"])          # ...e sobrescreve com os dados salvos
    mapa = estado["mapa"]

    # ---- compatibilidade com saves de versões anteriores ----
    for espaco in heroi.ESPACOS:                 # espaços novos (ex.: 2º acessório)
        heroi.equipamento.setdefault(espaco, None)
    if "equipamento" not in estado["heroi"]:     # antes do equipamento por espaço
        migrar_save_antigo(heroi)
    for sala in mapa.values():                   # antes as salas tinham um "item" só
        if "item" in sala:
            item = sala.pop("item")
            sala["itens"] = [item] if item else []

    andar = estado.get("andar", dados.PRIMEIRO_ANDAR)   # saves antigos não tinham andar
    return heroi, andar, estado["sala"], mapa
