# ============================================================================
#  batalha.py - o combate por turnos
# ============================================================================
#  Uma rodada:
#    1. turno do herói: escolhe uma ação (ou perde a vez se estiver preso)
#       - veneno: 1 de dano depois da ação
#    2. turno do inimigo: inimigo.agir() - cada tipo de inimigo age do seu jeito
#       - veneno: mais 1 de dano
#    3. o herói recupera energia
#
#  Efeitos do HERÓI diminuem no fim do turno dele; os do INIMIGO, no início do turno dele.
# ============================================================================

import random

from golpes import resolver_golpe
from itens import (adicionar_item, contar_consumiveis, elemento_da_arma, menu_usar,
                   nome_item, sortear_item, tentar_reviver)

CHANCE_FUGA = 0.5
SURTO_PERMITE_DEFESA = True  # as ações extras do Surto de Ação podem ser esquivar/bloquear?
DANO_VENENO_ARMA = 2         # veneno da Glândula (o mesmo da aranha)
DURACAO_VENENO_ARMA = 3

NOMES_EFEITOS = {"veneno": "Envenenado", "queimadura": "Queimando", "preso": "Preso",
                 "vulneravel": "Exposto", "atordoado": "Atordoado"}

# Efeitos que causam dano a cada ação: texto para o herói e para o inimigo
DANO_CONTINUO = {
    "veneno": ("O veneno arde", "O veneno corrói"),
    "queimadura": ("As queimaduras ardem", "O fogo consome"),
}


def vitoria(heroi, inimigo):
    print(f"\n  {inimigo.nome} foi derrotado! +{inimigo.xp} XP, +{inimigo.ouro} de ouro.")
    heroi.ouro += inimigo.ouro
    heroi.abates[inimigo.nome] = heroi.abates.get(inimigo.nome, 0) + 1
    heroi.ganhar_xp(inimigo.xp)
    heroi.postura = None
    heroi.efeitos = {}                       # efeitos acabam com a luta
    drops = ([inimigo.drop] if inimigo.drop else []) + list(inimigo.drops_extras)
    if inimigo.drop_tabela:                  # ex.: o Lich deixa também UMA relíquia sorteada
        drops.append(sortear_item(inimigo.drop_tabela, heroi))
    for drop in drops:
        if drop:
            print(f"  Entre os restos, você encontra: {nome_item(drop)}!")
            adicionar_item(heroi, drop)
    return "venceu"


def heroi_caiu(heroi):
    """True se o herói morreu de vez (um item de reviver pode salvá-lo)."""
    return not heroi.esta_vivo() and not tentar_reviver(heroi)


def aplicar_dano_continuo(personagem):
    """Veneno, queimadura... Chamado depois de CADA ação (herói e inimigo)."""
    for efeito, (texto_heroi, texto_inimigo) in DANO_CONTINUO.items():
        if personagem.efeitos.get(efeito) and personagem.esta_vivo():
            dano = personagem.dano_continuo.get(efeito, 1)
            personagem.receber_dano(dano)
            if hasattr(personagem, "energia"):   # é o herói
                print(f"  {texto_heroi}: {dano} de dano. Vida: {personagem.vida}/{personagem.vida_max}")
            else:
                print(f"  {texto_inimigo} {personagem.nome}: {dano} de dano.")


def aplicar_efeito(alvo, efeito, turnos, dano=None):
    """Aplica (ou renova, sem acumular) um efeito. dano: para efeitos de dano contínuo."""
    alvo.efeitos[efeito] = turnos
    if dano is not None:
        alvo.dano_continuo[efeito] = dano


def golpe_fisico(heroi, inimigo, dano, texto, alcance=1, chance_atordoar_extra=0.0):
    """Um golpe com a arma (ataque normal ou habilidade física) e tudo que a arma faz:
    elemento (fogo), roubo de vida, veneno e atordoamento."""
    reacao = resolver_golpe(inimigo, dano, texto, alcance=alcance, elemento=elemento_da_arma(heroi),
                            fisico=True)
    if reacao == "esquivou":
        return reacao

    if heroi.roubo_vida and inimigo.ultimo_dano:
        curou = heroi.curar(max(1, round(inimigo.ultimo_dano * heroi.roubo_vida)))
        if curou:
            print(f"  Sua arma bebe a vida de {inimigo.nome}: +{curou}. Vida: {heroi.vida}/{heroi.vida_max}")

    if not inimigo.esta_vivo():
        return reacao
    if heroi.arma_envenenada and not inimigo.imune_veneno:
        if "veneno" not in inimigo.efeitos:
            print(f"  O veneno da sua arma entra no corpo de {inimigo.nome}!")
        aplicar_efeito(inimigo, "veneno", DURACAO_VENENO_ARMA, DANO_VENENO_ARMA)
    # chance da arma e da habilidade juntas: só falha se as duas falharem
    chance = 1 - (1 - heroi.chance_atordoar) * (1 - chance_atordoar_extra)
    if chance and random.random() < chance:
        congela = elemento_da_arma(heroi) == "gelo"
        if inimigo.resiste_controle:
            print(f"  {inimigo.nome} cambaleia, mas resiste!")
        else:
            inimigo.efeitos["atordoado"] = 1
            if congela:
                print(f"  O frio congela {inimigo.nome}! Ele vai perder o próximo turno.")
            else:
                print(f"  O impacto atordoa {inimigo.nome}! Ele vai perder o próximo turno.")
    return reacao


def texto_efeitos(personagem):
    if not personagem.efeitos:
        return ""
    lista = ", ".join(f"{NOMES_EFEITOS.get(e, e)} ({t})" for e, t in personagem.efeitos.items())
    return f"  [{lista}]"


def mostrar_menu(heroi, inimigo):
    proxima_esquiva = heroi.chance_esquiva_ativa(heroi.esquivas_seguidas + 1)
    print(f"\n  {heroi.nome:<14} {heroi.barra_de_vida()}  Energia: {heroi.energia}/{heroi.energia_max}"
          f"{texto_efeitos(heroi)}")
    print(f"  {inimigo.nome:<14} {inimigo.barra_de_vida()}{texto_efeitos(inimigo)}")
    print(f"  1 - Atacar   2 - {heroi.nome_habilidade} ({heroi.custo_habilidade} energia"
          f"{heroi.info_habilidade()})   "
          f"3 - Usar item ({contar_consumiveis(heroi)})")
    print(f"  4 - Esquivar ({proxima_esquiva:.0%})   "
          f"5 - Bloquear (-{heroi.reducao_bloqueio:.0%} de dano)   6 - Fugir")
    return proxima_esquiva


def turno_do_heroi(heroi, inimigo):
    """O turno inteiro do herói. Retorna "fugiu" ou True.
    Com o Surto de Ação, o herói faz mais ações em seguida."""
    resultado = pedir_acao(heroi, inimigo)
    if resultado != "surto":
        return resultado
    total = heroi.acoes_extras_habilidade
    for numero in range(1, total + 1):
        if not inimigo.esta_vivo():
            break
        resultado = pedir_acao(heroi, inimigo, extra=(numero, total))
        if resultado == "fugiu":
            return "fugiu"
    return True


def pedir_acao(heroi, inimigo, extra=None):
    """Lê e executa UMA ação. Retorna "fugiu", "surto" ou True.
    Ações que não gastam turno (opção inválida, sem energia...) pedem de novo.
    extra = (número, total) quando é uma ação extra do Surto de Ação."""
    while True:
        proxima_esquiva = mostrar_menu(heroi, inimigo)
        if extra:
            acao = input(f"  Ação extra {extra[0]}/{extra[1]}: ").strip()
        else:
            acao = input("  Ação: ").strip()

        if extra and acao in ("4", "5") and not SURTO_PERMITE_DEFESA:
            print("  No embalo do Surto de Ação, não dá pra parar e se defender!")
            continue

        if acao == "1":
            golpe_fisico(heroi, inimigo, heroi.calcular_dano(inimigo), f"Você ataca {inimigo.nome}.")
        elif acao == "2":
            if extra and heroi.acoes_extras_habilidade:
                print(f"  Você já está no meio de um {heroi.nome_habilidade}!")
                continue
            if heroi.energia < heroi.custo_habilidade:
                print("  Energia insuficiente!")
                continue
            heroi.energia -= heroi.custo_habilidade
            if heroi.acoes_extras_habilidade:              # Surto de Ação: não ataca, dá ações
                heroi.postura = None
                heroi.esquivas_seguidas = 0
                print(f"  {heroi.nome} respira fundo: {heroi.nome_habilidade.upper()}! "
                      f"Você vai agir {heroi.acoes_extras_habilidade} vezes.")
                return "surto"
            dano, texto = heroi.usar_habilidade(inimigo)   # polimorfismo: cada classe faz a sua
            if heroi.elemento_habilidade:                  # magia: não usa a arma
                reacao = resolver_golpe(inimigo, dano, texto, alcance=heroi.alcance_habilidade,
                                        elemento=heroi.elemento_habilidade)
            else:                                          # habilidade física: usa a arma
                reacao = golpe_fisico(heroi, inimigo, dano, texto, alcance=heroi.alcance_habilidade,
                                      chance_atordoar_extra=heroi.atordoar_habilidade)
            heroi.apos_habilidade(acertou=(reacao != "esquivou"))
        elif acao == "3":
            if not menu_usar(heroi, inimigo):
                continue                         # não usou nada: não gasta o turno
        elif acao == "4":
            heroi.postura = "esquivar"
            heroi.esquivas_seguidas += 1
            print(f"  Você se prepara para desviar ({proxima_esquiva:.0%} de chance).")
        elif acao == "5":
            heroi.postura = "bloquear"
            print("  Você ergue a guarda.")
        elif acao == "6":
            if inimigo.chefe:
                print("  Uma barreira mágica bloqueia a saída! Não há como fugir.")
                continue
            if random.random() < CHANCE_FUGA:
                print("  Você consegue fugir!")
                return "fugiu"
            print("  Você tenta fugir, mas não consegue!")
        else:
            print("  Opção inválida.")
            continue

        if acao != "4":
            heroi.esquivas_seguidas = 0          # qualquer outra ação zera a penalidade
        if acao not in ("4", "5"):
            heroi.postura = None
        return True


CURAS = ("pocao", "pocao_grande")


def combate(heroi, inimigo):
    """Retorna 'venceu', 'fugiu' ou 'morreu'. Anota um resumo da luta em heroi.lutas
    (vai para o histórico de partidas no progresso.json)."""
    vida_antes = heroi.vida
    curas_antes = sum(heroi.inventario.get(c, 0) for c in CURAS)
    resultado = lutar(heroi, inimigo)
    heroi.lutas.append({
        "inimigo": inimigo.nome, "resultado": resultado, "nivel": heroi.nivel,
        "vida": f"{vida_antes} -> {heroi.vida}/{heroi.vida_max}",
        "pocoes": curas_antes - sum(heroi.inventario.get(c, 0) for c in CURAS),
        "turnos": heroi.turnos_na_luta,
    })
    return resultado


def lutar(heroi, inimigo):
    print(f"\n  !!! {inimigo.texto_aparece()} !!!")
    heroi.turnos_na_luta = 0
    heroi.preparar_para_combate()
    heroi.ultimo_inimigo = inimigo.nome
    turno_inimigo = 0          # só conta quando o inimigo age (marca o ritmo dos especiais)

    if inimigo.embosca:        # ex.: mímico: ataca antes de você reagir
        print(f"  Você foi pego de surpresa!")
        turno_inimigo += 1
        inimigo.agir(heroi, turno_inimigo)
        if heroi_caiu(heroi):
            return "morreu"

    while True:
        # ---- turno do herói ----
        heroi.turnos_na_luta += 1
        heroi.curou_no_turno = False
        preso = heroi.efeitos.pop("preso", None)
        tonto = heroi.efeitos.pop("atordoado", None)
        if preso or tonto:
            heroi.postura = None
            heroi.esquivas_seguidas = 0
            motivo = "se debate na teia" if preso else "ainda está tonto"
            print(f"\n  {heroi.nome} {motivo} e perde o turno!")
        elif turno_do_heroi(heroi, inimigo) == "fugiu":
            heroi.efeitos = {}
            return "fugiu"
        aplicar_dano_continuo(heroi)
        aplicar_dano_continuo(inimigo)
        heroi.passar_turno_efeitos()

        if heroi_caiu(heroi):
            return "morreu"
        if not inimigo.esta_vivo():
            return vitoria(heroi, inimigo)

        # ---- turno do inimigo ----
        atordoado = inimigo.efeitos.pop("atordoado", None)
        inimigo.passar_turno_efeitos()
        if atordoado:
            print(f"  {inimigo.nome} está atordoado e perde o turno!")
        else:
            turno_inimigo += 1                   # turno perdido não conta para os especiais
            inimigo.agir(heroi, turno_inimigo)   # polimorfismo: cada inimigo age do seu jeito
        aplicar_dano_continuo(heroi)
        aplicar_dano_continuo(inimigo)

        if heroi_caiu(heroi):
            heroi.postura = None
            return "morreu"
        if not inimigo.esta_vivo():              # pode morrer no contra-ataque
            return vitoria(heroi, inimigo)

        heroi.recuperar_energia(heroi.energia_por_turno())
