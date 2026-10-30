# ============================================================================
#  jogo.py - exploração: andar pelas salas e interpretar os comandos
# ============================================================================

import random

import batalha
import caido
import dados
from itens import comprar, menu_equipar, menu_usar, mostrar_inventario, pegar_itens, usar_item, vender
from mapa import DIRECOES, criar_mapa, descrever_sala, mostrar_mapa, sala_inicial, tentar_andar
from inimigos import criar_inimigo
from personagens import CLASSES
from save import salvar

AJUDA = """
  Comandos:
    norte, sul, leste, oeste (ou n, s, l, o)  - andar
    olhar      - descrever a sala de novo
    pegar      - pegar os itens da sala
    status     - ver seu personagem
    inventario - ver equipamento e mochila (ou i)
    equipar    - equipar/trocar um item da mochila
    usar       - usar um item (poção, éter...)
    pocao      - beber uma poção de vida
    mapa       - ver o mapa da masmorra
    comprar    - comprar itens (onde houver mercador)
    vender     - vender itens da mochila pela metade do valor (onde houver mercador)
    beber      - beber da fonte (onde houver uma)
    abrir      - abrir um baú (cuidado...)
    falar      - conversar com quem estiver na sala
    salvar     - salvar e sair (pausa a partida; ao continuar, o save é usado e apagado)
    sair       - sair (pergunta se quer salvar; sem salvar, a partida é perdida)
"""


def fala_do_npc(npc, heroi):
    """Se você derrotou alguém que o NPC tem algo a dizer ("falas_abates"), ele comenta
    (uma vez cada, na ordem do JSON). Depois disso, volta às falas de sempre,
    que passam a incluir também esses comentários.

    As falas de sempre saem de um "saco": embaralha todas, tira uma por vez e só
    embaralha de novo quando o saco esvazia. Assim nenhuma se repete antes de
    todas as outras terem saído."""
    sobre_abates = npc.get("falas_abates", {})
    comentados = npc.setdefault("comentados", [])   # fica no mapa: entra no save
    for nome, fala in sobre_abates.items():
        if heroi.abates.get(nome) and nome not in comentados:
            comentados.append(nome)
            return fala

    todas = npc["falas"] + [sobre_abates[nome] for nome in comentados]
    saco = npc.setdefault("saco", [])               # as que ainda não saíram nesta rodada
    novas = [f for f in todas if f not in saco and f not in npc.get("ditas", [])]
    saco.extend(novas)                              # comentário novo entra na rodada atual
    if not saco:                                    # todas já saíram: nova rodada
        saco.extend(todas)
        npc["ditas"] = []
    fala = random.choice(saco)
    if len(saco) > 1 and fala == npc.get("ultima"):  # na virada, não repete a última dita
        fala = random.choice([f for f in saco if f != fala])
    saco.remove(fala)
    npc.setdefault("ditas", []).append(fala)
    npc["ultima"] = fala
    return fala


def entrar_na_sala(heroi, mapa, sala_id):
    """Descreve a sala e dispara o combate se tiver inimigo.
    Retorna 'venceu', 'venceu_chefe', 'fugiu', 'morreu' ou None (sem luta)."""
    sala = mapa[sala_id]
    descrever_sala(sala)

    resultado = None
    if sala.get("inimigo"):
        inimigo = criar_inimigo(sala["inimigo"])
        resultado = batalha.combate(heroi, inimigo)
        if resultado == "venceu":
            sala["inimigo"] = None               # não aparece de novo
            if inimigo.chefe:
                if inimigo.texto_derrota:
                    print("\n  " + inimigo.texto_derrota.replace("\n", "\n  "))
                return "venceu_chefe"
    if resultado in (None, "venceu") and sala.get("caido"):
        resultado = enfrentar_caido(heroi, sala)
    return resultado


def enfrentar_caido(heroi, sala):
    """Um herói de uma partida anterior, que voltou como morto-vivo (ou já virou Lich)."""
    caido_id = sala["caido"]
    sala["caido"] = None                         # vencendo ou fugindo, não volta nesta partida
    registro = caido.buscar(caido.carregar_lista(), caido_id)
    if not registro:
        return None
    if registro["lich"]:
        print(f"\n  No meio da sala, sobre os restos de {sala.get('vitima_do_lich', 'algo')}, "
              f"uma figura de coroa se vira devagar.")
        print(f"  '{sala.get('vitima_do_lich', 'Ele')} não foi páreo. Eu estava esperando por VOCÊ.'")
        print(f"  É {caido.nome_completo(registro)}.")
    else:
        print(f"\n  Passos arrastados. Uma figura de {registro['classe'].lower()} se ergue das sombras,")
        print(f"  usando um equipamento que você conhece bem. É {caido.nome_completo(registro)}.")
    resultado = batalha.combate(heroi, caido.criar_inimigo_caido(registro, heroi))
    caido.apos_encontro(caido_id, resultado)
    return resultado


def abrir_bau(heroi, sala):
    """Abre o baú da sala. Se for um mímico, luta. Retorna o resultado da luta (ou None)."""
    bau = sala.get("bau")
    if not bau:
        print("  Não há baú aqui.")
        return None
    resultado = None
    if bau["mimico"]:
        print("  Você toca a tampa... e ela se abre sozinha, cheia de DENTES!")
        resultado = batalha.combate(heroi, criar_inimigo("mimico"))
        if resultado != "venceu":
            return resultado                     # se fugir, o mímico continua lá
    else:
        print("  O baú range e se abre.")
    sala["bau"] = None
    if bau["itens"]:
        sala["itens"].extend(bau["itens"])
        print("  Algo caiu no chão. (pegar)")
    else:
        print("  Está vazio.")
    return resultado


def executar_comando(comando, heroi, mapa, sala_atual, andar):
    """Comandos que não mudam de sala. Retorna True para continuar,
    ou "pausou"/"abandonou" para encerrar a partida."""
    """Comandos que não mudam de sala. Retorna False se o comando for 'sair'."""
    sala = mapa[sala_atual]

    if comando == "olhar":
        descrever_sala(sala)
    elif comando == "pegar":
        pegar_itens(heroi, sala)
    elif comando == "equipar":
        menu_equipar(heroi)
    elif comando == "usar":
        menu_usar(heroi)
    elif comando == "status":
        heroi.mostrar_status()
    elif comando in ("inventario", "inventário", "i"):
        mostrar_inventario(heroi)
    elif comando in ("pocao", "poção"):
        usar_item(heroi, "pocao")
    elif comando == "mapa":
        mostrar_mapa(sala, andar)
    elif comando == "comprar":
        mercador = sala.get("mercador")
        if mercador is True:                     # saves da versão antiga usavam True
            mercador = {"pocao": 10}
        if mercador:
            comprar(heroi, mercador)
        else:
            print("  Não há ninguém vendendo nada aqui.")
    elif comando == "vender":
        if sala.get("mercador"):
            vender(heroi)
        else:
            print("  Não há ninguém para comprar nada aqui.")
    elif comando == "beber":
        if sala.get("fonte"):
            heroi.vida = heroi.vida_max
            heroi.energia = heroi.energia_max
            sala["fonte"] = False                # cada fonte só pode ser usada uma vez
            print("  A água gelada percorre seu corpo. Vida e energia restauradas!")
            print("  O brilho da água se apaga. Ela não vai ajudar de novo.")
        else:
            print("  Não há nada para beber aqui.")
    elif comando == "falar":
        npc = sala.get("npc")
        if npc:
            print(f"\n  {npc['nome']}: \"{fala_do_npc(npc, heroi)}\"")
        else:
            print("  Não há ninguém para conversar aqui. Você fala sozinho por um tempo.")
    elif comando == "salvar":
        salvar(heroi, sala_atual, mapa, andar)
        print("  Partida pausada. Ela continua de onde parou na próxima vez.")
        return "pausou"
    elif comando == "ajuda":
        print(AJUDA)
    elif comando == "sair":
        resposta = input("  Salvar e sair? Sem salvar, a partida é PERDIDA. (s/n) ").strip().lower()
        if resposta == "s":
            salvar(heroi, sala_atual, mapa, andar)
            print("  Partida pausada.")
            return "pausou"
        if input("  Tem certeza que quer abandonar a partida? (s/n) ").strip().lower() == "s":
            print(f"  {heroi.nome} dá as costas para a masmorra...")
            return "abandonou"
    elif comando != "":
        print("  Comando desconhecido. Digite 'ajuda' para ver os comandos.")
    return True


def jogar(heroi, sala_atual, mapa, andar):
    """Joga UM andar. Retorna "morreu", "venceu_chefe", "pausou" ou "abandonou"."""
    resultado = entrar_na_sala(heroi, mapa, sala_atual)
    sala_anterior = sala_atual

    while True:
        # ---- o que aconteceu ao entrar na última sala ----
        if resultado == "morreu":
            print(f"\n  {heroi.nome} caiu na escuridão da masmorra...")
            print("  ========== FIM DE JOGO ==========")
            return "morreu"
        if resultado == "fugiu":
            print("  Você volta correndo para a sala anterior.")
            sala_atual = sala_anterior
            descrever_sala(mapa[sala_atual])
        if resultado == "venceu_chefe":
            return "venceu_chefe"
        resultado = None

        # ---- lê um comando ----
        comando = input("\n> ").strip().lower()

        if comando in DIRECOES:
            destino = tentar_andar(heroi, mapa, sala_atual, DIRECOES[comando])
            if destino:
                sala_anterior, sala_atual = sala_atual, destino
                resultado = entrar_na_sala(heroi, mapa, sala_atual)
        elif comando == "abrir":
            resultado = abrir_bau(heroi, mapa[sala_atual])
            if resultado == "fugiu":                # fugiu do mímico: fica na mesma sala
                print("  Você se afasta do baú.")
                resultado = None
        else:
            saida = executar_comando(comando, heroi, mapa, sala_atual, andar)
            if saida is not True:
                return saida


def jogar_campanha(heroi, andar, sala_atual=None, mapa=None):
    """Joga a partir de um andar e vai descendo até o fim.
    Sem sala/mapa, começa o andar do zero.
    Retorna "morreu", "venceu", "pausou" ou "abandonou"."""
    if mapa is None:
        mapa = criar_mapa(heroi, andar)
        caido.colocar_no_mapa(mapa, andar)
        sala_atual = sala_inicial(andar)
        print(f"\n  ~~~ {dados.info_andar(andar)['nome']} ~~~")
        print(f"  {dados.info_andar(andar)['intro']}")

    while True:
        resultado = jogar(heroi, sala_atual, mapa, andar)
        if resultado == "morreu" and heroi.revivido:
            caido.registrar(heroi, andar)       # morreu depois do Filactério: vira o Desmorto
        if resultado != "venceu_chefe":
            return resultado
        heroi.andares_concluidos.append(andar)

        proximo = dados.proximo_andar(andar)
        if proximo is None:                      # era o último andar
            print(f"\n  ===== VITÓRIA! {heroi.nome} chegou ao nível {heroi.nivel} "
                  f"com {heroi.ouro} de ouro. =====")
            return "venceu"

        # ---- passagem para o próximo andar ----
        print(f"\n  ===== {dados.info_andar(andar)['nome']}: CONCLUÍDO =====")
        print(f"  {dados.info_andar(andar)['conclusao']}")
        heroi.vida, heroi.energia = heroi.vida_max, heroi.energia_max
        print("  Você descansa antes de descer. Vida e energia restauradas.")

        andar = proximo
        mapa = criar_mapa(heroi, andar)
        caido.colocar_no_mapa(mapa, andar)
        sala_atual = sala_inicial(andar)
        print(f"\n  ~~~ {dados.info_andar(andar)['nome']} ~~~")
        print(f"  {dados.info_andar(andar)['intro']}")


def criar_personagem():
    nome = ""
    while not nome:
        nome = input("\nQual o nome do seu herói? ").strip()

    print("\nEscolha sua classe:")
    nomes_classes = list(CLASSES)
    for numero, nome_classe in enumerate(nomes_classes, 1):
        print(f"  {numero} - {nome_classe}: {CLASSES[nome_classe].descricao}")

    while True:
        escolha = input("Classe: ").strip()
        # funciona com qualquer quantidade de classes, não só 3
        if escolha.isdigit() and 1 <= int(escolha) <= len(nomes_classes):
            classe = CLASSES[nomes_classes[int(escolha) - 1]]
            return classe(nome)
        print(f"Escolha um número de 1 a {len(nomes_classes)}.")
