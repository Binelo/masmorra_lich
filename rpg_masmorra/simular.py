# ============================================================================
#  simular.py - testa o balanceamento jogando muitas partidas automáticas
# ============================================================================
#  Uso:   py simular.py              (300 partidas, herói sem melhorias do Santuário)
#         py simular.py 1000         (mais partidas = mais preciso, mais lento)
#         py simular.py 300 max      (com TODAS as melhorias do Santuário compradas)
#
#  O "jogador robô" joga a campanha inteira (todos os andares), seguindo uma
#  rota fixa por andar. Rode sempre que mudar números de classes, inimigos ou itens.
#  Se mudar um mapa, atualize a rota daquele andar em ROTAS.
# ============================================================================

import builtins
import contextlib
import io
import os
import random
import sys
import tempfile
from collections import defaultdict

import batalha
import caido
import itens
import dados
import progresso
import golpes
import jogo
import save
from personagens import CLASSES

# Nunca mexer no save de verdade durante a simulação
save.ARQUIVO_SAVE = os.path.join(tempfile.gettempdir(), "rpg_masmorra_simulacao.json")
caido.ATIVO = False          # nem criar nem encontrar heróis caídos
progresso.ATIVO = False      # não mexe nos seus Ecos

TODAS_AS_MELHORIAS = {m["id"]: len(m["custos"]) for m in progresso.MELHORIAS}

# Rota de cada andar: explora tudo (a chave é sorteada), pega os itens, usa as
# recompensas dos mini-chefes e termina no chefe.
ROTAS = {
    "cripta": [
        "n",                                  # salão (rato)
        "l", "pegar",                         # arsenal (esqueleto)
        "l", "pegar",                         # caverna (morcegos)
        "n", "pegar", "usar", "glandula",     # ninho (aranha) -> envenena a arma
        "s", "o", "o", "o", "pegar",          # biblioteca
        "o", "comprar", "pocao",              # laboratório
        "n", "pegar", "equipar", "coracao",   # ponte (troll)
        "l", "pegar",                         # cripta (zumbi)
        "s", "l", "n", "pegar",               # corredor (goblin)
        "l", "beber", "o",                    # fonte
        "n",                                  # trono (Lich)
        "equipar", "filacterio",              # garante o Filactério no lugar do Coração
    ],
    "minas": [
        "l", "falar",                         # loja do Kyrzathul
        "comprar", "{item_da_classe}", "equipar", "{item_da_classe}",
        "comprar", "pocao_grande", "comprar", "unguento", "comprar", "bomba_gelo",
        "n", "pegar",                         # poço de lava (elemental)
        "n", "pegar",                         # fornalha (berserker)
        "o", "pegar",                         # salão dos reis (Capataz)
        "o", "pegar", "beber",                # forja (golem) + água
        "s", "pegar", "abrir", "pegar",       # depósito (aranha + baú)
        "s", "pegar",                         # trilhos (morcegos)
        "l", "n", "pegar", "abrir", "pegar",  # barracas (kobolds + baú)
        "n", "o", "beber", "l",               # volta à forja pra recuperar
        "n",                                  # covil (Ignarax)
    ],
}

ultimo_texto = ""

# O que cada classe compra do Kyrzathul ("{item_da_classe}" na rota)
ITEM_DA_CLASSE = {"Guerreiro": "armadura_escamas", "Mago": "tomo_inverno", "Ladino": "anel_predador"}

ESTRATEGIAS = {
    "joga_bem": "joga bem (equipa, vende, compra, cura)",
    "segue_dica": "segue as dicas dos inimigos",
    "ignora": "ignora as dicas",
    "so_ataca": "só ataca (e toma poção)",
}


# ---------------------------------------------------------------- robô "joga bem"
# Joga como uma pessoa atenta: segue as dicas, equipa o melhor que achar, vende o
# que sobra, compra poções, cura entre as lutas e gasta bombas nos chefes.

PESOS = {"ataque": 3, "defesa": 3, "vida_max": 0.6, "esquiva": 50, "reducao_bloqueio": 25,
         "energia_max": 0.4, "poder": 2.5, "CHANCE_CRITICO": 30, "roubo_vida": 25,
         "cura_defensiva": 3, "chance_atordoar": 15, "espinhos": 1.5, "resistencia_fogo": 8,
         "furia": 12, "acoes_extras_habilidade": 15}


def nota_do_item(heroi, chave):
    """Quanto um equipamento vale pra ESTE herói (pra decidir o que equipar)."""
    if chave is None:
        return 0
    item = itens.ITENS[chave]
    if not itens.pode_equipar(heroi, chave):
        return -1
    nota = 0
    for atributo, valor in item.get("bonus", {}).items():
        if atributo == "poder" and not hasattr(heroi, "poder"):
            continue
        nota += PESOS.get(atributo, 1) * valor
    nota += 20 if item.get("reviver") else 0
    nota += 2 if item.get("elemento") else 0
    nota += 15 if item.get("troca_habilidade") else 0
    return nota


def equipar_o_melhor(heroi, luta):
    melhorou = True
    while melhorou:
        melhorou = False
        for chave in [c for c, q in heroi.inventario.items() if q > 0 and itens.eh_equipamento(c)]:
            espacos = itens.espacos_possiveis(chave)
            pior = min(espacos, key=lambda e: nota_do_item(heroi, heroi.equipamento.get(e)))
            if nota_do_item(heroi, chave) > nota_do_item(heroi, heroi.equipamento.get(pior)) + 0.5:
                luta["trocar"] = str(espacos.index(pior) + 1)
                itens.equipar(heroi, chave)
                melhorou = True
                break


def curar_fora_de_combate(heroi):
    while heroi.vida < heroi.vida_max * 0.6:
        falta = heroi.vida_max - heroi.vida
        ordem = ("pocao_grande", "pocao") if falta >= 50 else ("pocao", "pocao_grande")
        chave = next((c for c in ordem if heroi.inventario.get(c, 0) > 0), None)
        if not chave:
            return
        itens.usar_item(heroi, chave)


def fazer_compras(heroi, mercador):
    """Vende o equipamento que sobrou na mochila e compra poções (e bombas de gelo)."""
    for chave, qtd in list(heroi.inventario.items()):
        preco = itens.preco_venda(chave)
        if qtd > 0 and itens.eh_equipamento(chave) and preco:
            heroi.inventario[chave] = 0
            heroi.ouro += preco * qtd
    desejos = [("pocao_grande", 4), ("pocao", 4), ("bomba_gelo", 2), ("antidoto", 1), ("unguento", 1)]
    comprou = True
    while comprou:
        comprou = False
        for chave, maximo in desejos:
            if chave in mercador and heroi.inventario.get(chave, 0) < maximo and heroi.ouro >= mercador[chave]:
                heroi.ouro -= mercador[chave]
                itens.adicionar_item(heroi, chave)
                comprou = True


def escolher_acao(estrategia, heroi, inimigo, texto_recente, luta):
    """O 'cérebro' do jogador robô. texto_recente = o que apareceu desde a última ação.
    Para usar um item, devolve "3" e guarda qual em luta["item"]."""
    tem = lambda item: heroi.inventario.get(item, 0) > 0
    def usar(item):
        luta["item"] = item
        return "3"

    vida_baixa = heroi.vida < heroi.vida_max * 0.35 and tem("pocao")
    tem_energia = heroi.energia >= heroi.custo_habilidade
    # não gasta habilidade em quem é imune ao elemento dela (ex.: Bola de Fogo no Elemental)
    if heroi.elemento_habilidade and inimigo.fraquezas.get(heroi.elemento_habilidade, 1) == 0:
        tem_energia = False
    vem_especial = golpes.DICA_ESQUIVAR in texto_recente or golpes.DICA_BLOQUEAR in texto_recente

    if estrategia == "joga_bem":
        if vem_especial and tem("pergaminho_gelo") and inimigo.chefe:
            return usar("pergaminho_gelo")       # congela bem na hora do especial
        limite = 0.5 if inimigo.chefe else 0.4       # contra chefe, cura mais cedo
        if heroi.vida < heroi.vida_max * (0.25 if vem_especial else limite):
            falta = heroi.vida_max - heroi.vida
            for cura in (("pocao_grande", "pocao") if falta >= 45 else ("pocao", "pocao_grande")):
                if tem(cura):
                    return usar(cura)
        if (inimigo.chefe or inimigo.resiste_controle) and not vem_especial:
            for bomba in ("bomba_gelo", "bomba"):
                elemento = itens.ITENS[bomba]["elemento"]
                if tem(bomba) and inimigo.fraquezas.get(elemento, 1) >= 1:
                    return usar(bomba)
    if estrategia in ("segue_dica", "joga_bem") and vem_especial:
        defesa = "4" if golpes.DICA_ESQUIVAR in texto_recente else "5"
        if heroi.acoes_extras_habilidade and tem_energia and batalha.SURTO_PERMITE_DEFESA:
            luta["defesa_no_fim"] = defesa      # Surto: ataca e termina se defendendo
            return "2"
        return defesa
    if vida_baixa:
        return usar("pocao")
    if estrategia == "so_ataca":
        return "1"
    for efeito, cura in (("veneno", "antidoto"), ("queimadura", "unguento")):
        if efeito in heroi.efeitos and tem(cura) and heroi.vida < heroi.vida_max * 0.6:
            return usar(cura)
    # contra enxame: área primeiro (habilidade com alcance, senão bomba)
    if hasattr(inimigo, "vivos") and inimigo.vivos() >= 3:
        if heroi.alcance_habilidade > 1 and tem_energia:
            return "2"
        for bomba in ("bomba", "bomba_gelo"):
            if tem(bomba):
                return usar(bomba)
    return "2" if tem_energia else "1"


def acao_extra(heroi, prompt, luta):
    """Ações extras do Surto de Ação: ataca, e termina se defendendo se vier um especial."""
    numero, total = prompt.strip().split()[-1].rstrip(":").split("/")
    if numero == total and "defesa_no_fim" in luta:
        return luta.pop("defesa_no_fim")
    if heroi.vida < heroi.vida_max * 0.35 and heroi.inventario.get("pocao", 0) > 0:
        luta["item"] = "pocao"
        return "3"
    return "1"


def jogar_partida(classe, estrategia, semente, melhorias=None):
    """Joga a campanha inteira.
    Retorna (venceu, lutas, andares_concluidos); lutas = {inimigo: (dano %, turnos)}."""
    random.seed(semente)
    heroi = classe("Robô")
    if melhorias:
        with contextlib.redirect_stdout(io.StringIO()):
            progresso.aplicar_melhorias(heroi, melhorias)
    item_classe = ITEM_DA_CLASSE.get(classe.__name__, "pocao_grande")
    comandos = iter([c.replace("{item_da_classe}", item_classe)
                     for andar in dados.ANDARES for c in ROTAS.get(andar["id"], [])])
    saida = io.StringIO()
    lido_ate = 0
    lutas = {}
    luta = {"inimigo": None}

    # mede o dano recebido em cada luta
    receber_original = heroi.receber_dano
    def receber_dano(dano):
        if luta["inimigo"] is not None:
            luta["dano"] += min(dano, heroi.vida)
        receber_original(dano)
    heroi.receber_dano = receber_dano

    def input_falso(prompt=""):
        nonlocal lido_ate
        texto = saida.getvalue()
        p = prompt.strip()
        if luta["inimigo"] is not None and p == "Ação:":
            luta["turnos"] += 1
            acao = escolher_acao(estrategia, heroi, luta["inimigo"], texto[lido_ate:], luta)
        elif luta["inimigo"] is not None and p.startswith("Ação extra"):
            acao = acao_extra(heroi, p, luta)
        elif p == "Trocar qual?":
            acao = luta.pop("trocar", "1")
        elif luta["inimigo"] is not None and p == "Item:":
            acao = luta.pop("item", "pocao")
        else:
            acao = next(comandos)            # StopIteration quando a rota acaba
            if estrategia == "joga_bem" and acao in ("n", "s", "l", "o"):
                with contextlib.redirect_stdout(io.StringIO()):
                    equipar_o_melhor(heroi, luta)
                    if sala_atual["sala"] and sala_atual["sala"].get("mercador"):
                        fazer_compras(heroi, sala_atual["sala"]["mercador"])
                    curar_fora_de_combate(heroi)
        saida.write(prompt)
        lido_ate = len(saida.getvalue())
        return acao

    sala_atual = {"sala": None}
    descrever_original = jogo.descrever_sala
    def descrever_e_lembrar(sala):
        sala_atual["sala"] = sala
        descrever_original(sala)

    combate_original = batalha.combate
    def combate_medido(h, inimigo):
        luta.update(inimigo=inimigo, dano=0, turnos=0)
        vida_max_no_inicio = h.vida_max          # pode subir de nível durante a luta
        try:
            return combate_original(h, inimigo)
        finally:
            lutas[inimigo.nome] = (luta["dano"] / vida_max_no_inicio, luta["turnos"])
            luta["inimigo"] = None

    input_original = builtins.input
    builtins.input, batalha.combate, jogo.descrever_sala = input_falso, combate_medido, descrever_e_lembrar
    try:
        with contextlib.redirect_stdout(saida):
            jogo.jogar_campanha(heroi, dados.PRIMEIRO_ANDAR)
    except StopIteration:
        pass
    finally:
        builtins.input, batalha.combate, jogo.descrever_sala = input_original, combate_original, descrever_original

    texto = saida.getvalue()
    global ultimo_texto
    ultimo_texto = texto                       # útil pra investigar uma partida específica
    concluidos = [a["id"] for a in dados.ANDARES if f"{a['nome']}: CONCLUÍDO" in texto]
    venceu = "VITÓRIA" in texto
    if venceu:
        concluidos.append(dados.ANDARES[-1]["id"])
    return venceu, lutas, concluidos


def chefe_do_andar(andar_id):
    """Nome do chefe de um andar (o inimigo com "chefe": true no mapa dele)."""
    for sala in dados.MAPAS[andar_id]["salas"].values():
        chave = sala.get("inimigo")
        if chave and dados.INIMIGOS[chave].get("chefe"):
            return dados.INIMIGOS[chave]["nome"]


def main():
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 300
    melhorias = TODAS_AS_MELHORIAS if "max" in sys.argv[2:] else None
    andares = [a["id"] for a in dados.ANDARES if a["id"] in ROTAS]
    print(f"Simulando {n} partidas por classe e estratégia ({len(andares)} andar(es)), "
          f"{'com TODAS as melhorias do Santuário' if melhorias else 'sem melhorias do Santuário'}...\n")

    resultados = {}
    for estrategia in ESTRATEGIAS:
        for nome, classe in CLASSES.items():
            resultados[estrategia, nome] = [jogar_partida(classe, estrategia, s, melhorias) for s in range(n)]

    for andar in andares:
        info = dados.info_andar(andar)
        chefe = chefe_do_andar(andar)
        anterior = andares[andares.index(andar) - 1] if andares.index(andar) > 0 else None
        def chegaram(r):
            """Partidas que começaram este andar (concluíram o anterior)."""
            return [x for x in r if anterior is None or anterior in x[2]]

        print(f"===== {info['nome']} =====")
        if anterior:
            print("(porcentagens entre quem chegou a este andar)")
        print(f"{'':<36}" + "".join(f"{nome:>11}" for nome in CLASSES))
        for estrategia, descricao in ESTRATEGIAS.items():
            linha = f"{descricao[:27] + ': conclui':<36}"
            for nome in CLASSES:
                r = chegaram(resultados[estrategia, nome])
                linha += f"{sum(andar in c for _, _, c in r) / len(r):>11.0%}" if r else f"{'-':>11}"
            print(linha)
        linha = f"{'jogando bem: chega ao chefe':<36}"
        for nome in CLASSES:
            r = chegaram(resultados["joga_bem", nome])
            linha += f"{sum(chefe in l for _, l, _ in r) / len(r):>11.0%}" if r else f"{'-':>11}"
        print(linha)

        # curva de dificuldade do andar (jogando bem)
        inimigos_do_andar = []
        for sala in dados.MAPAS[andar]["salas"].values():
            if sala.get("inimigo"):
                nome_inimigo = dados.INIMIGOS[sala["inimigo"]]["nome"]
                if nome_inimigo not in inimigos_do_andar:
                    inimigos_do_andar.append(nome_inimigo)
        print("\nDano recebido em cada luta (% da vida máxima) e turnos, jogando bem:")
        for inimigo in inimigos_do_andar:
            linha = f"{inimigo[:20]:<22}"
            for nome in CLASSES:
                valores = [l[inimigo] for _, l, _ in resultados["joga_bem", nome] if inimigo in l]
                if valores:
                    dano = sum(v[0] for v in valores) / len(valores)
                    turnos = sum(v[1] for v in valores) / len(valores)
                    linha += f"{dano:>9.0%} {turnos:>4.1f}t"
                else:
                    linha += f"{'-':>15}"
            print(linha)
        print()


if __name__ == "__main__":
    main()
