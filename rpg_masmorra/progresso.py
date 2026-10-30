# ============================================================================
#  progresso.py - o que sobrevive entre as partidas: Ecos e o Santuário
# ============================================================================
#  A morte é permanente, mas a alma do herói deixa ECOS. No fim de cada partida
#  (morrendo, vencendo ou abandonando) os Ecos são somados, e no Santuário você
#  os troca por melhorias permanentes, que valem para todos os heróis seguintes.
#
#  As melhorias ficam em dados/santuario.json. Tipos:
#    "atributo": "vida_max", "por_nivel": 5     soma no atributo do herói
#    "item": "pocao", "por_nivel": 1            começa com itens a mais
#    "ouro": 15                                 começa com ouro a mais (por nível)
#    "tabela_inicial": "armas"                  começa com um item sorteado da tabela
# ============================================================================

import json
import os

import dados
from itens import adicionar_item, nome_item, sortear_item

ARQUIVO = os.path.join(dados.PASTA, "progresso.json")
ATIVO = True                                   # o simulador desliga isso
MELHORIAS = dados.carregar_json("santuario.json")

# Como os Ecos são calculados no fim da partida
ECOS_POR_XP = 1 / 5            # 1 Eco a cada 5 de XP ganho
ECOS_POR_ANDAR = 20            # por andar concluído
ECOS_POR_VITORIA = 40          # bônus por vencer a campanha inteira


def carregar():
    padrao = {"ecos": 0, "melhorias": {}, "partidas": 0, "vitorias": 0, "ecos_totais": 0}
    if not ATIVO or not os.path.exists(ARQUIVO):
        return padrao
    try:
        with open(ARQUIVO, "r", encoding="utf-8") as arquivo:
            return {**padrao, **json.load(arquivo)}
    except (json.JSONDecodeError, OSError):
        return padrao


def salvar(progresso):
    if not ATIVO:
        return
    with open(ARQUIVO, "w", encoding="utf-8") as arquivo:
        json.dump(progresso, arquivo, indent=2, ensure_ascii=False)


# ---------------------------------------------------------------- aplicar no herói

def aplicar_melhorias(heroi, niveis=None):
    """Aplica as melhorias compradas num herói recém-criado.
    niveis: {id: nível}; se None, usa as do progresso salvo."""
    if niveis is None:
        niveis = carregar()["melhorias"]
    for melhoria in MELHORIAS:
        nivel = niveis.get(melhoria["id"], 0)
        if nivel <= 0:
            continue
        quantidade = melhoria["por_nivel"] * nivel
        if "atributo" in melhoria and hasattr(heroi, melhoria["atributo"]):
            atributo = melhoria["atributo"]
            setattr(heroi, atributo, getattr(heroi, atributo) + quantidade)
            if atributo == "vida_max":
                heroi.vida = heroi.vida_max
            if atributo == "energia_max":
                heroi.energia = heroi.energia_max
        if "item" in melhoria:
            heroi.inventario[melhoria["item"]] = heroi.inventario.get(melhoria["item"], 0) + quantidade
        if "ouro" in melhoria:
            heroi.ouro += melhoria["ouro"] * nivel
        if "tabela_inicial" in melhoria:
            for _ in range(nivel):
                item = sortear_item(melhoria["tabela_inicial"], heroi)
                if item:
                    print(f"  Herança: você começa com {nome_item(item)}.")
                    adicionar_item(heroi, item)


# ---------------------------------------------------------------- fim de partida

def calcular_ecos(heroi, venceu):
    ecos = round(heroi.xp_total * ECOS_POR_XP)
    ecos += ECOS_POR_ANDAR * len(heroi.andares_concluidos)
    if venceu:
        ecos += ECOS_POR_VITORIA
    return ecos


def fim_de_partida(heroi, resultado):
    """Chamado quando a partida acaba de vez (morreu, venceu ou abandonou)."""
    progresso = carregar()
    ecos = calcular_ecos(heroi, resultado == "venceu")
    progresso["ecos"] += ecos
    progresso["ecos_totais"] += ecos
    progresso["partidas"] += 1
    if resultado == "venceu":
        progresso["vitorias"] += 1
    salvar(progresso)

    print("\n  ---------------- FIM DA PARTIDA ----------------")
    print(f"  {heroi.nome}, o {type(heroi).__name__} - nível {heroi.nivel}")
    print(f"  Andares concluídos: {len(heroi.andares_concluidos)} | "
          f"Inimigos derrotados: {sum(heroi.abates.values())}")
    print(f"  A alma de {heroi.nome} deixa {ecos} Ecos. Total guardado: {progresso['ecos']}.")
    print("  -------------------------------------------------")


# ---------------------------------------------------------------- Santuário

def custo_proximo(melhoria, nivel):
    return melhoria["custos"][nivel] if nivel < len(melhoria["custos"]) else None


def santuario():
    """Menu entre partidas para gastar os Ecos."""
    while True:
        progresso = carregar()
        niveis = progresso["melhorias"]
        print("\n  ============ SANTUÁRIO ============")
        print("  Os ecos dos que caíram antes de você sussurram aqui.")
        print(f"  Ecos: {progresso['ecos']}   (partidas: {progresso['partidas']}, vitórias: {progresso['vitorias']})\n")
        for numero, melhoria in enumerate(MELHORIAS, 1):
            nivel = niveis.get(melhoria["id"], 0)
            maximo = len(melhoria["custos"])
            custo = custo_proximo(melhoria, nivel)
            preco = f"{custo} Ecos" if custo is not None else "MÁXIMO"
            print(f"  {numero} - {melhoria['nome']:<16} [{nivel}/{maximo}] {melhoria['descricao']:<62} {preco}")
        print("  0 - Voltar")

        escolha = input("  Melhorar: ").strip()
        if escolha in ("", "0"):
            return
        if not escolha.isdigit() or not 1 <= int(escolha) <= len(MELHORIAS):
            print("  Opção inválida.")
            continue
        melhoria = MELHORIAS[int(escolha) - 1]
        nivel = niveis.get(melhoria["id"], 0)
        custo = custo_proximo(melhoria, nivel)
        if custo is None:
            print("  Essa melhoria já está no máximo.")
        elif progresso["ecos"] < custo:
            print(f"  Faltam {custo - progresso['ecos']} Ecos.")
        else:
            progresso["ecos"] -= custo
            niveis[melhoria["id"]] = nivel + 1
            salvar(progresso)
            print(f"  {melhoria['nome']} agora está no nível {nivel + 1}.")
