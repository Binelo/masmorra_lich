# ============================================================================
#  golpes.py - como um golpe é resolvido (usado por heróis, inimigos e itens)
# ============================================================================

from personagens import Heroi

CONTRA_ATAQUE = True        # esquiva ATIVA bem-sucedida devolve um ataque normal
LIMIAR_DICA_ESQUIVA = 0.6   # a partir dessa chance de esquiva ativa, as dicas sugerem desviar

DICA_ESQUIVAR = "Seus instintos dizem que, atento, dá pra sair do caminho."
DICA_BLOQUEAR = "Melhor estar com a guarda erguida."


def bom_de_esquiva(heroi):
    # Decide pelo ATRIBUTO, não pelo nome da classe: uma classe nova ou um item
    # que aumente a esquiva já muda as dicas sem precisar mexer aqui.
    return heroi.chance_esquiva_ativa(1) >= LIMIAR_DICA_ESQUIVA


def resolver_golpe(alvo, dano, texto, so_esquiva_ativa=False, inesquivavel=False,
                   alcance=1, elemento=None, atacante=None, fisico=False):
    """Aplica um golpe no alvo, narra o resultado e devolve a reação
    ("esquivou", "bloqueou" ou None)."""
    postura_do_alvo = alvo.postura
    alvo.notas = []
    recebido, reacao = alvo.receber_ataque(dano, so_esquiva_ativa=so_esquiva_ativa,
                                           inesquivavel=inesquivavel,
                                           alcance=alcance, elemento=elemento, fisico=fisico)
    if reacao == "esquivou":
        msg = f"  {texto} Mas {alvo.nome} se esquiva!"
    elif reacao == "bloqueou":
        msg = f"  {texto} {alvo.nome} bloqueia e recebe só {recebido} de dano."
    else:
        msg = f"  {texto} {alvo.texto_dano(recebido)}"
    if isinstance(alvo, Heroi):
        msg += f" Vida: {alvo.vida}/{alvo.vida_max}"
    alvo.ultimo_dano = recebido if reacao != "esquivou" else 0
    print(msg.rstrip())
    for nota in alvo.notas:                      # frases extras: "Você foi envenenado!" etc.
        print(f"  {nota}")
    alvo.notas = []

    # Espinhos: o herói que foi acertado devolve dano a quem bateu
    if (isinstance(alvo, Heroi) and atacante and reacao != "esquivou"
            and alvo.espinhos and atacante.esta_vivo()):
        atacante.receber_dano(alvo.espinhos)
        print(f"  Os espinhos ferem {atacante.nome}: {alvo.espinhos} de dano.")

    # Contra-ataque: só quando o alvo esquivou DE PROPÓSITO (não vale a passiva)
    if CONTRA_ATAQUE and reacao == "esquivou" and postura_do_alvo == "esquivar" and atacante:
        contra = alvo.calcular_dano(atacante)
        resolver_golpe(atacante, contra, f"{alvo.nome} aproveita a abertura e contra-ataca!",
                       fisico=True)
    return reacao
