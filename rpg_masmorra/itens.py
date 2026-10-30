# ============================================================================
#  itens.py - itens: pegar, equipar, usar, comprar e listar
# ============================================================================
#  Os itens ficam em dados/itens.json. Dois tipos:
#
#  EQUIPAMENTO (tem "espaco"):
#    "espaco": "arma" | "escudo" | "armadura" | "acessorio"
#    "bonus": {"ataque": 3, "esquiva": -0.05}   soma ao equipar, tira ao desequipar
#    "classes": ["Mago"]                        (opcional) quem pode usar
#
#  "valor": 20            preço de referência; vender paga a metade
#  "vendivel": false      não pode ser vendido (itens especiais, chave)
#
#  CONSUMÍVEL ("tipo": "consumivel"), some ao usar:
#    "cura": 30       recupera vida
#    "energia": 15    recupera energia
#    "dano": 20       dano direto no inimigo (só em combate, não dá pra desviar)
#      "alcance": 99    ...em quantos alvos (enxames); "elemento": "fogo"
#    "cura_efeito": "veneno"  remove um efeito (veneno, queimadura...)
#    "envenena_arma": true seus golpes passam a envenenar (permanente)
#    "congelar": true      o inimigo perde o próximo turno (funciona até em chefes)
#    "congela_alvo": true  (com "dano") depois da explosão, o inimigo perde o turno (chefes e mini-chefes resistem)
#
#  EFEITOS ESPECIAIS DE EQUIPAMENTO:
#    "elemento": "fogo"          (arma) seus golpes físicos viram fogo
#    "reviver": 0.4              (qualquer) ao morrer, volta com 40% da vida e o item quebra
#    "troca_habilidade": {"nome_habilidade": "Lança de Gelo", "elemento_habilidade": "gelo"}
#                                muda a habilidade enquanto estiver equipado
#    bonus em roubo_vida, chance_atordoar, espinhos, cura_defensiva: veja personagens.py
# ============================================================================

import random

import dados
from golpes import resolver_golpe

ITENS = dados.ITENS


# ---------------------------------------------------------------- consultas

def nome_item(chave):
    return ITENS[chave]["nome"]


def eh_equipamento(chave):
    return "espaco" in ITENS[chave]


def eh_consumivel(chave):
    return ITENS[chave].get("tipo") == "consumivel"


def pode_equipar(heroi, chave):
    classes = ITENS[chave].get("classes")
    return classes is None or type(heroi).__name__ in classes


def descrever_bonus(chave):
    return ITENS[chave]["descricao"]


# Um tipo de item pode caber em mais de um espaço do corpo (2 acessórios)
ESPACOS_DO_TIPO = {"acessorio": ["acessorio", "acessorio_2"]}
NOMES_ESPACOS = {"arma": "Arma", "escudo": "Escudo", "armadura": "Armadura",
                 "acessorio": "Acessório 1", "acessorio_2": "Acessório 2"}


def espacos_possiveis(chave):
    tipo = ITENS[chave]["espaco"]
    return ESPACOS_DO_TIPO.get(tipo, [tipo])


def espaco_livre(heroi, chave):
    """O primeiro espaço vazio onde o item cabe, ou None."""
    return next((e for e in espacos_possiveis(chave) if heroi.equipamento.get(e) is None), None)


def elemento_da_arma(heroi):
    arma = heroi.equipamento.get("arma")
    return ITENS[arma].get("elemento") if arma else None


def sortear_item(tabela, heroi=None, ja_sorteados=()):
    """Sorteia um item da tabela, respeitando os pesos. Ignora:
    - itens que a classe do herói não pode usar (um Guerreiro nunca acha um cajado)
    - equipamentos que já saíram nesta partida (não aparecem dois escudos)
    Consumíveis podem repetir."""
    pesos = dados.SAQUE[tabela]
    def permitido(chave):
        if not eh_equipamento(chave):
            return True
        if chave in ja_sorteados:
            return False
        if heroi is not None and (heroi.inventario.get(chave, 0) > 0
                                  or chave in heroi.equipamento.values()):
            return False                       # o herói já tem esse equipamento
        return heroi is None or pode_equipar(heroi, chave)
    opcoes = [c for c in pesos if permitido(c)]
    if not opcoes:
        return None
    # random.choices sorteia com pesos: peso 6 sai 3x mais que peso 2
    return random.choices(opcoes, weights=[pesos[c] for c in opcoes])[0]



def tentar_reviver(heroi):
    """Se o herói tiver um item com "reviver" equipado, volta à vida e o item quebra."""
    for espaco, chave in heroi.equipamento.items():
        if chave and ITENS[chave].get("reviver"):
            aplicar_bonus(heroi, ITENS[chave].get("bonus", {}), -1)
            trocar_habilidade(heroi, chave, desfazer=True)
            heroi.equipamento[espaco] = None
            heroi.vida = max(1, round(heroi.vida_max * ITENS[chave]["reviver"]))
            heroi.revivido = True
            print(f"\n  {nome_item(chave)} se despedaça e uma luz fria te puxa de volta! "
                  f"Vida: {heroi.vida}/{heroi.vida_max}")
            return True
    return False


# ---------------------------------------------------------------- equipamento

def aplicar_bonus(heroi, bonus, sinal):
    """sinal = +1 para equipar, -1 para desequipar."""
    for atributo, valor in bonus.items():
        if not hasattr(heroi, atributo):       # ex.: "poder" num herói que não é Mago
            continue
        novo = getattr(heroi, atributo) + sinal * valor
        # round evita lixo de ponto flutuante (0.33 + 0.05 - 0.05 = 0.33000000000000007)
        setattr(heroi, atributo, round(novo, 4) if isinstance(novo, float) else novo)

    # Ganhar vida/energia máxima também enche aquela parte; perder não pode deixar acima do máximo
    if sinal > 0:
        heroi.vida += bonus.get("vida_max", 0)
        heroi.energia += bonus.get("energia_max", 0)
    heroi.vida = min(heroi.vida, heroi.vida_max)
    heroi.energia = min(heroi.energia, heroi.energia_max)


def trocar_habilidade(heroi, chave, desfazer=False):
    """Itens com "troca_habilidade" mudam atributos da habilidade (ex.: Bola de Fogo vira
    Lança de Gelo). Desfazer apaga o atributo do OBJETO e volta o valor da CLASSE."""
    for atributo, valor in ITENS[chave].get("troca_habilidade", {}).items():
        if desfazer:
            vars(heroi).pop(atributo, None)
        else:
            setattr(heroi, atributo, valor)


def escolher_espaco_para_trocar(heroi, chave):
    """Todos os espaços do item estão ocupados: pergunta qual trocar (se houver mais de um)."""
    candidatos = espacos_possiveis(chave)
    if len(candidatos) == 1:
        return candidatos[0]
    print(f"  Os dois espaços estão ocupados. Trocar qual por {nome_item(chave)}?")
    for numero, espaco in enumerate(candidatos, 1):
        print(f"    {numero} - {nome_item(heroi.equipamento[espaco])} ({NOMES_ESPACOS[espaco]})")
    print("    0 - Nenhum")
    resposta = input("  Trocar qual? ").strip()
    if resposta.isdigit() and 1 <= int(resposta) <= len(candidatos):
        return candidatos[int(resposta) - 1]
    return None


def equipar(heroi, chave):
    """Tira o item da mochila e coloca num espaço dele. O que estava lá volta pra mochila."""
    if not pode_equipar(heroi, chave):
        classes = " ou ".join(ITENS[chave]["classes"])
        print(f"  Só {classes} sabe usar {nome_item(chave)}.")
        return False

    espaco = espaco_livre(heroi, chave) or escolher_espaco_para_trocar(heroi, chave)
    if espaco is None:
        print("  Você deixa tudo como estava.")
        return False
    anterior = heroi.equipamento.get(espaco)
    if anterior:
        aplicar_bonus(heroi, ITENS[anterior]["bonus"], -1)
        heroi.inventario[anterior] = heroi.inventario.get(anterior, 0) + 1

    if anterior:
        trocar_habilidade(heroi, anterior, desfazer=True)
    heroi.inventario[chave] -= 1
    heroi.equipamento[espaco] = chave
    aplicar_bonus(heroi, ITENS[chave]["bonus"], +1)
    trocar_habilidade(heroi, chave)

    if anterior:
        print(f"  Você troca {nome_item(anterior)} por {nome_item(chave)}.")
    else:
        print(f"  Você equipa {nome_item(chave)}.")
    return True


def menu_equipar(heroi):
    opcoes = [c for c, q in heroi.inventario.items() if q > 0 and eh_equipamento(c)]
    if not opcoes:
        print("  Você não tem nada para equipar na mochila.")
        return
    print("\n  Equipar:")
    for numero, chave in enumerate(opcoes, 1):
        candidatos = espacos_possiveis(chave)
        if espaco_livre(heroi, chave):
            troca = ""
        elif len(candidatos) == 1:
            troca = f" (no lugar de {nome_item(heroi.equipamento[candidatos[0]])})"
        else:
            troca = " (escolhe qual acessório trocar)"
        aviso = "" if pode_equipar(heroi, chave) else " [sua classe não pode usar]"
        print(f"    {numero} - {nome_item(chave)}: {descrever_bonus(chave)}{troca}{aviso}")
    print("    0 - Nada")
    chave = escolher(opcoes, "  Equipar: ")
    if chave:
        equipar(heroi, chave)


# ---------------------------------------------------------------- pegar / comprar

def adicionar_item(heroi, chave):
    """Coloca na mochila. Equipamento vai direto pro corpo se o espaço estiver livre."""
    heroi.inventario[chave] = heroi.inventario.get(chave, 0) + 1
    if eh_equipamento(chave):
        if espaco_livre(heroi, chave) and pode_equipar(heroi, chave):
            equipar(heroi, chave)
        elif not espaco_livre(heroi, chave):
            print(f"  (Os espaços para isso estão ocupados. Use 'equipar' para trocar.)")


def pegar_itens(heroi, sala):
    if not sala["itens"]:
        print("  Não há nada para pegar aqui.")
        return
    for chave in sala["itens"]:
        print(f"  Você pegou: {nome_item(chave)}. {descrever_bonus(chave)}")
        adicionar_item(heroi, chave)
    sala["itens"] = []


def comprar(heroi, mercador):
    """mercador é um dict {item: preço}, vindo da sala no mapa.json."""
    produtos = list(mercador)
    print("\n  'O que vai querer, aventureiro?'")
    for numero, chave in enumerate(produtos, 1):
        aviso = "" if not eh_equipamento(chave) or pode_equipar(heroi, chave) else " [sua classe não pode usar]"
        print(f"    {numero} - {nome_item(chave)} ({mercador[chave]} de ouro) - {descrever_bonus(chave)}{aviso}")
    print("    0 - Nada")
    print(f"  Seu ouro: {heroi.ouro}")

    chave = escolher(produtos, "  Comprar: ")
    if not chave:
        return
    preco = mercador[chave]
    if heroi.ouro < preco:
        print(f"  '{nome_item(chave)} custa {preco} de ouro. Volte quando tiver.'")
        return
    heroi.ouro -= preco
    print(f"  Você compra: {nome_item(chave)}. Ouro restante: {heroi.ouro}")
    adicionar_item(heroi, chave)


def preco_venda(chave):
    item = ITENS[chave]
    if item.get("vendivel") is False or "valor" not in item:
        return None
    return item["valor"] // 2                  # metade do valor, arredondando pra baixo


def vender(heroi):
    """Vende um item da MOCHILA (o que está equipado não aparece aqui)."""
    opcoes = [c for c, q in heroi.inventario.items() if q > 0 and preco_venda(c) is not None]
    if not opcoes:
        print("  'Você não tem nada que me interesse, aventureiro.'")
        return
    print("\n  'Deixa eu ver o que você tem...'")
    for numero, chave in enumerate(opcoes, 1):
        print(f"    {numero} - {nome_item(chave)} x{heroi.inventario[chave]} "
              f"({preco_venda(chave)} de ouro cada)")
    print("    0 - Nada")
    print("  (Itens equipados não aparecem. Para vender um, troque-o antes com 'equipar'.)")

    chave = escolher(opcoes, "  Vender: ")
    if not chave:
        return
    heroi.inventario[chave] -= 1
    heroi.ouro += preco_venda(chave)
    print(f"  Você vende {nome_item(chave)} por {preco_venda(chave)} de ouro. Ouro: {heroi.ouro}")


# ---------------------------------------------------------------- consumíveis

def usar_item(heroi, chave, inimigo=None):
    """Usa um consumível. Retorna True se foi usado (gasta o turno no combate)."""
    item = ITENS[chave]
    if heroi.inventario.get(chave, 0) == 0:
        print(f"  Você não tem {nome_item(chave)}.")
        return False

    if item.get("congelar"):
        if inimigo is None:
            print("  Melhor guardar isso para um combate.")
            return False
        inimigo.efeitos["atordoado"] = 1
        print(f"  Uma rajada de gelo envolve {inimigo.nome}! Ele vai perder o próximo turno.")
    elif item.get("envenena_arma"):
        if heroi.arma_envenenada:
            print("  Sua arma já está envenenada.")
            return False
        heroi.arma_envenenada = True
        print(f"  Você espreme {nome_item(chave)} sobre a lâmina. Seus golpes agora envenenam!")
    elif item.get("cura_efeito") or item.get("cura_veneno"):
        efeito = item.get("cura_efeito", "veneno")
        if efeito not in heroi.efeitos:
            print(f"  Você não está com {efeito}.")
            return False
        del heroi.efeitos[efeito]
        print(f"  Você usa {nome_item(chave)}. A {efeito} some.")
    elif "cura" in item:
        if heroi.vida == heroi.vida_max:
            print("  Sua vida já está cheia.")
            return False
        curou = heroi.curar(item["cura"])
        print(f"  Você usa {nome_item(chave)} e recupera {curou} de vida. Vida: {heroi.vida}/{heroi.vida_max}")
    elif "energia" in item:
        if heroi.energia == heroi.energia_max:
            print("  Sua energia já está cheia.")
            return False
        antes = heroi.energia
        heroi.recuperar_energia(item["energia"])
        print(f"  Você usa {nome_item(chave)} e recupera {heroi.energia - antes} de energia. "
              f"Energia: {heroi.energia}/{heroi.energia_max}")
    elif "dano" in item:
        if inimigo is None:
            print("  Melhor guardar isso para um combate.")
            return False
        resolver_golpe(inimigo, item["dano"], f"A {nome_item(chave)} explode em {inimigo.nome}!",
                       inesquivavel=True, alcance=item.get("alcance", 1), elemento=item.get("elemento"))
        if item.get("congela_alvo") and inimigo.esta_vivo():
            if inimigo.resiste_controle:
                print(f"  {inimigo.nome} sacode o gelo de cima de si.")
            else:
                inimigo.efeitos["atordoado"] = 1
                print(f"  O gelo prende {inimigo.nome}! Ele vai perder o próximo turno.")
    else:
        print("  Nada acontece.")
        return False

    heroi.inventario[chave] -= 1
    return True


def menu_usar(heroi, inimigo=None):
    """Lista os consumíveis e usa o escolhido. Retorna True se usou algum."""
    opcoes = [c for c, q in heroi.inventario.items() if q > 0 and eh_consumivel(c)]
    if not opcoes:
        print("  Você não tem itens para usar.")
        return False
    print("\n  Usar:")
    for numero, chave in enumerate(opcoes, 1):
        print(f"    {numero} - {nome_item(chave)} x{heroi.inventario[chave]}: {descrever_bonus(chave)}")
    print("    0 - Nada")
    chave = escolher(opcoes, "  Item: ")
    return usar_item(heroi, chave, inimigo) if chave else False


def contar_consumiveis(heroi):
    return sum(q for c, q in heroi.inventario.items() if q > 0 and eh_consumivel(c))


# ---------------------------------------------------------------- listagem

def mostrar_inventario(heroi):
    print("\n  Equipado:")
    for espaco, chave in heroi.equipamento.items():
        texto = f"{nome_item(chave)} - {descrever_bonus(chave)}" if chave else "(vazio)"
        print(f"    {NOMES_ESPACOS.get(espaco, espaco):<12} {texto}")

    print("  Mochila:")
    mochila = {k: v for k, v in heroi.inventario.items() if v > 0}
    if not mochila:
        print("    (vazia)")
    for chave, quantidade in mochila.items():
        print(f"    {nome_item(chave)} x{quantidade} - {descrever_bonus(chave)}")
    print(f"  Ouro: {heroi.ouro}")


# ---------------------------------------------------------------- utilidades

def escolher(opcoes, mensagem):
    """Lê um número (ou o nome do item) e devolve a chave escolhida, ou None."""
    resposta = input(mensagem).strip().lower()
    if resposta in opcoes:                      # aceita o nome direto: "pocao"
        return resposta
    if resposta.isdigit() and 1 <= int(resposta) <= len(opcoes):
        return opcoes[int(resposta) - 1]
    if resposta not in ("", "0"):
        print("  Opção inválida.")
    return None


def migrar_save_antigo(heroi):
    """Saves de antes do equipamento por espaço: espada/escudo estavam no inventário
    com o bônus já aplicado. Move para o equipamento SEM aplicar o bônus de novo."""
    for chave in list(heroi.inventario):
        if heroi.inventario[chave] > 0 and eh_equipamento(chave):
            espaco = espaco_livre(heroi, chave)
            if espaco:
                heroi.equipamento[espaco] = chave
                heroi.inventario[chave] -= 1
