# ============================================================================
#  caido.py - os heróis caídos (Desmortos) e como eles viram Liches
# ============================================================================
#  A história: o Filactério devolve a vida, mas cobra um preço. Quem morre DEPOIS
#  de ter sido revivido por ele não descansa: volta como morto-vivo e, se não
#  for destruído, aos poucos se torna um Lich.
#
#  Regras:
#  - Morrer depois de ser revivido pelo Filactério registra o herói em caido.json
#    (no máximo 3; um novo substitui o mais antigo que ainda não virou Lich).
#  - Num mapa novo, cada caído daquele andar tem a SUA chance de aparecer
#    (começa em 60%), numa sala sorteada. Quem não aparece continua na lista.
#  - Fugir dele: chance -20 pontos (mínimo 10%), +1 passo rumo a Lich, +10% de força.
#  - Derrotar: chance de voltar (15%, +10% a cada derrota, até 45%). Se voltar,
#    também ganha +1 passo. Se não voltar, descansa e sai da lista.
#  - 3 passos: vira LICH, mas só se não houver outro Lich-caído (um por vez;
#    os outros ficam parados até ele ser derrotado).
#  - O Lich-caído mata um mini-chefe do andar e toma a sala dele. Derrotado,
#    deixa ouro, itens, um Filactério e uma relíquia melhorada.
# ============================================================================

import json
import os
import random
import time

import dados
from inimigos import Desmorto, Inimigo
from itens import ITENS, sortear_item

ARQUIVO = os.path.join(dados.PASTA, "caido.json")
ATIVO = True                 # o simulador desliga isso

MAXIMO = 3
CHANCE_INICIAL = 0.6
CHANCE_MINIMA = 0.1
QUEDA_POR_FUGA = 0.2
FORCA_INICIAL = 0.8          # 80% da vida e do ataque que o herói tinha
FORCA_POR_PASSO = 0.1
PASSOS_PARA_LICH = 3
VOLTA_BASE, VOLTA_POR_DERROTA, VOLTA_MAXIMA = 0.15, 0.10, 0.45
NAO_VAI_PRO_CAIDO = ("chave", "chave_covil")   # itens de missão não contam

# ---------------------------------------------------------------- títulos

TITULOS_POR_ITEM = {
    "adaga_vampirica": "o Bebedor de Sangue", "foice_sombria": "o Bebedor de Sangue",
    "foice_sombria_plus": "o Bebedor de Sangue",
    "lamina_flamejante": "o Incandescente", "presa_ignarax": "o Incandescente",
    "lamina_gelida": "o Coração de Gelo", "tomo_inverno": "o Coração de Gelo",
    "martelo": "o Trovejante", "armadura_espinhos": "o Espinhento",
    "coracao": "o de Carne Teimosa", "machado": "o Lenhador",
    "escudo_torre": "a Muralha", "nucleo_golem": "o de Ferro",
}
TITULOS_POR_ABATE = {
    "O Lich": "o Matador de Liches", "Ignarax": "o Matador de Dragões",
    "Troll da Ponte": "o Caçador de Trolls", "Aranha Gigante": "o Caçador de Aranhas",
    "Capataz Anão": "o Quebra-Escudos",
}


def escolher_titulo(heroi):
    """Sorteia um título entre os que combinam com a partida do herói."""
    opcoes = [TITULOS_POR_ITEM[i] for i in heroi.equipamento.values() if i in TITULOS_POR_ITEM]
    opcoes += [titulo for nome, titulo in TITULOS_POR_ABATE.items() if heroi.abates.get(nome)]
    if heroi.arma_envenenada:
        opcoes.append("o Envenenador")
    if heroi.ouro >= 150:
        opcoes.append("o Avarento")
    if heroi.nivel <= 3:
        opcoes.append("o Imprudente")
    if sum(heroi.abates.values()) >= 12:
        opcoes.append("o Incansável")
    return random.choice(opcoes) if opcoes else "o Desmorto"


# ---------------------------------------------------------------- arquivo

def carregar_lista():
    if not ATIVO or not os.path.exists(ARQUIVO):
        return []
    try:
        with open(ARQUIVO, "r", encoding="utf-8") as arquivo:
            conteudo = json.load(arquivo)
    except (json.JSONDecodeError, OSError):
        return []
    if isinstance(conteudo, dict) and "caidos" not in conteudo:     # formato antigo: um caído só
        conteudo = {"caidos": [completar(conteudo)]}
    return [completar(r) for r in conteudo["caidos"]]


def completar(registro):
    """Preenche campos que registros mais antigos não tinham."""
    padrao = {"id": f"{registro.get('nome', '?')}-antigo", "titulo": "o Desmorto",
              "chance": CHANCE_INICIAL, "passos": 0, "forca": FORCA_INICIAL,
              "derrotas": 0, "lich": False}
    return {**padrao, **registro}


def salvar_lista(lista):
    if not ATIVO:
        return
    if not lista:
        if os.path.exists(ARQUIVO):
            os.remove(ARQUIVO)
        return
    with open(ARQUIVO, "w", encoding="utf-8") as arquivo:
        json.dump({"caidos": lista}, arquivo, indent=2, ensure_ascii=False)


def buscar(lista, caido_id):
    return next((r for r in lista if r["id"] == caido_id), None)


def nome_completo(registro):
    return f"{registro['nome']}, o Lich" if registro["lich"] else f"{registro['nome']}, {registro['titulo']}"


# ---------------------------------------------------------------- registrar

def registrar(heroi, andar):
    """Guarda o herói que acabou de morrer (depois de ter sido revivido)."""
    if not ATIVO:
        return
    itens = [chave for chave, qtd in heroi.inventario.items() for _ in range(qtd)]
    itens += [chave for chave in heroi.equipamento.values() if chave]
    registro = completar({
        "id": f"{heroi.nome}-{int(time.time() * 1000)}",
        "nome": heroi.nome,
        "titulo": escolher_titulo(heroi),
        "classe": type(heroi).__name__,
        "andar": andar,
        "nivel": heroi.nivel,
        "vida_max": heroi.vida_max,
        "ataque": heroi.ataque,
        "defesa": heroi.defesa,
        "esquiva": heroi.esquiva,
        "reducao_bloqueio": heroi.reducao_bloqueio,
        "poder": getattr(heroi, "poder", 0),
        "ouro": heroi.ouro,
        "itens": [i for i in itens if i not in NAO_VAI_PRO_CAIDO],
    })
    lista = carregar_lista()
    if len(lista) >= MAXIMO:
        antigos = [r for r in lista if not r["lich"]]
        if antigos:
            lista.remove(antigos[0])           # o mais antigo que ainda não é Lich
    lista.append(registro)
    salvar_lista(lista)
    print(f"\n  ...mas a morte não é o fim para {heroi.nome}. O Filactério cobra seu preço:")
    print(f"  algo dele continua preso nestes corredores. Será lembrado como {nome_completo(registro)}.")


# ---------------------------------------------------------------- no mapa

def eh_mini_chefe(chave_inimigo):
    info = dados.INIMIGOS[chave_inimigo]
    return bool(info.get("drop")) and not info.get("chefe")


def colocar_no_mapa(mapa, andar):
    """Num mapa NOVO: decide quais caídos deste andar aparecem e onde."""
    inicio = dados.MAPAS[andar]["inicio"]
    for registro in carregar_lista():
        if registro["andar"] != andar:
            continue
        if registro["lich"]:
            # o Lich-caído matou um mini-chefe e tomou a sala dele
            salas = [sid for sid, s in mapa.items()
                     if s.get("inimigo") and eh_mini_chefe(s["inimigo"]) and not s.get("caido")]
            if salas:
                sala = mapa[random.choice(salas)]
                sala["vitima_do_lich"] = dados.INIMIGOS[sala["inimigo"]]["nome"]
                sala["inimigo"] = None
                sala["caido"] = registro["id"]
            continue
        if random.random() >= registro["chance"]:
            continue                            # não apareceu desta vez, continua na lista
        candidatas = [sid for sid, s in mapa.items()
                      if sid != inicio and not s.get("caido")
                      and not (s.get("inimigo") and dados.INIMIGOS[s["inimigo"]].get("chefe"))]
        if candidatas:
            mapa[random.choice(candidatas)]["caido"] = registro["id"]


# ---------------------------------------------------------------- inimigo

def metade_dos_itens(registro):
    itens = [i for i in registro["itens"] if i in ITENS]
    random.shuffle(itens)
    return itens[:(len(itens) + 1) // 2]            # metade, arredondando pra cima


def criar_inimigo_caido(registro, heroi=None):
    if registro["lich"]:
        return criar_lich_caido(registro, heroi)
    forca = registro["forca"]
    return Desmorto(
        nome=nome_completo(registro),
        classe=registro["classe"],
        vida=max(1, round(registro["vida_max"] * forca)),
        ataque=max(1, round(registro["ataque"] * forca)),
        defesa=registro["defesa"],
        esquiva=min(0.25, registro["esquiva"]),     # morto-vivo é mais duro, menos ágil
        reducao_bloqueio=registro["reducao_bloqueio"],
        poder=round(registro["poder"] * forca),
        xp=30 + 20 * registro["nivel"],
        ouro=registro["ouro"] // 2,
        imune_veneno=True,
        fraquezas={"fogo": 1.25},
        drops_extras=metade_dos_itens(registro),
        resiste_controle=True,
    )


def criar_lich_caido(registro, heroi=None):
    """Os atributos do Lich original (ajustados ao andar), com o ataque do herói
    se for maior, e o Raio Sombrio."""
    base = dict(dados.INIMIGOS["lich"])
    fator = dados.info_andar(registro["andar"]).get("forca_lich_caido", 1.0)
    reliquia = sortear_item("reliquias_lich_plus", heroi)
    return Inimigo(
        nome=nome_completo(registro),
        vida=round(base["vida"] * fator),
        ataque=max(round(base["ataque"] * fator), round(registro["ataque"] * registro["forca"])),
        defesa=round(base["defesa"] * fator),
        esquiva=base.get("esquiva", 0),
        xp=round(150 * fator),
        ouro=registro["ouro"] // 2 + 50,
        imune_veneno=True,
        fraquezas={"fogo": 1.25},
        especial=base["especial"],
        drops_extras=metade_dos_itens(registro) + ["filacterio"] + ([reliquia] if reliquia else []),
    )


# ---------------------------------------------------------------- depois do encontro

def avancar(registro, lista):
    """+1 passo rumo a Lich (se não houver outro Lich-caído segurando)."""
    outro_lich = any(r["lich"] for r in lista if r is not registro)
    if registro["passos"] >= PASSOS_PARA_LICH - 1 and outro_lich:
        print(f"  Algo mais antigo e mais forte segura {registro['nome']}: ele não consegue ir além... por enquanto.")
        return
    registro["passos"] += 1
    registro["forca"] = round(registro["forca"] + FORCA_POR_PASSO, 2)
    if registro["passos"] >= PASSOS_PARA_LICH:
        registro["lich"] = True
        print(f"  Você sente um frio na espinha. Em algum lugar, {registro['nome']} se ergue com uma coroa de ossos.")
        print(f"  Agora ele é {nome_completo(registro)}.")


def apos_encontro(caido_id, resultado):
    """Atualiza o caído depois da luta: 'venceu' (você venceu), 'fugiu' ou 'morreu'."""
    lista = carregar_lista()
    registro = buscar(lista, caido_id)
    if not registro or resultado == "morreu":
        return
    if resultado == "fugiu":
        if registro["lich"]:
            print(f"  {nome_completo(registro)} não tem pressa. Ele vai continuar esperando.")
        else:
            registro["chance"] = max(CHANCE_MINIMA, round(registro["chance"] - QUEDA_POR_FUGA, 2))
            print(f"  Às suas costas, {registro['nome']} ri. Cada fuga o deixa mais forte.")
            avancar(registro, lista)
    elif resultado == "venceu":
        if registro["lich"]:
            lista.remove(registro)
            print(f"  A coroa de ossos se parte. {registro['nome']} finalmente está livre.")
        else:
            chance_voltar = min(VOLTA_MAXIMA, VOLTA_BASE + VOLTA_POR_DERROTA * registro["derrotas"])
            registro["derrotas"] += 1
            if random.random() < chance_voltar:
                print(f"  Os ossos de {registro['nome']} se juntam de novo, lentamente... Ele vai voltar.")
                avancar(registro, lista)
            else:
                lista.remove(registro)
                print(f"  O espírito de {registro['nome']} finalmente descansa.")
    salvar_lista(lista)
