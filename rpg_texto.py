# ============================================================================
#  A MASMORRA DO LICH - um RPG de texto no terminal
# ============================================================================
#  Explore a masmorra, derrote os monstros, junte equipamentos e enfrente
#  o Lich na sala do trono.  Digite "ajuda" durante o jogo para ver os comandos.
#
#  Conceitos usados aqui:
#    - classes, herança e super()           (ex28, ex29)
#    - atributos de classe sobrescritos pelas subclasses (polimorfismo)
#    - dicionários aninhados para o mapa     (ex13)
#    - **kwargs para criar inimigos          (ex18)
#    - JSON para salvar e carregar o jogo    (ex26)
#    - try/except, random, f-strings, comprehensions
# ============================================================================

import json
import os
import random

# O save fica na mesma pasta do arquivo .py, não importa de onde você rode
PASTA = os.path.dirname(os.path.abspath(__file__))
ARQUIVO_SAVE = os.path.join(PASTA, "rpg_save.json")

PRECO_POCAO = 10
CURA_POCAO = 30


# ============================================================================
#  PERSONAGENS
# ============================================================================

class Personagem:
    """Base para heróis e inimigos: tudo que luta tem vida, ataque e defesa.

    Esquiva e bloqueio também ficam aqui, então heróis E inimigos ganham isso
    pela herança, sem código repetido.
    """

    # Valores padrão (as subclasses e os inimigos sobrescrevem)
    esquiva = 0.0             # chance de desviar de qualquer ataque (passiva)
    reducao_bloqueio = 0.0    # quanto do dano o bloqueio tira (0.3 = 30%)

    ESQUIVA_ATIVA_MULT = 2.5  # esquivar de propósito multiplica a chance passiva...
    ESQUIVA_ATIVA_MAX = 0.85  # ...até no máximo 85%
    PENALIDADE_SEGUIDA = 0.20 # cada esquiva ativa seguida tira 20% da chance

    def __init__(self, nome, vida_max, ataque, defesa):
        self.nome = nome
        self.vida_max = vida_max
        self.vida = vida_max
        self.ataque = ataque
        self.defesa = defesa
        self.postura = None           # None, "esquivar" ou "bloquear" (vale até o próximo turno)
        self.esquivas_seguidas = 0

    def esta_vivo(self):
        return self.vida > 0

    def calcular_dano(self, alvo, multiplicador=1, ignora_defesa=False):
        # Um pouco de sorte em cada golpe: ataque de -2 a +2
        base = (self.ataque + random.randint(-2, 2)) * multiplicador
        defesa = 0 if ignora_defesa else alvo.defesa
        return max(1, round(base) - defesa)    # sempre causa pelo menos 1

    def chance_esquiva_ativa(self, esquivas_seguidas):
        chance = min(self.ESQUIVA_ATIVA_MAX, self.esquiva * self.ESQUIVA_ATIVA_MULT)
        chance -= self.PENALIDADE_SEGUIDA * (esquivas_seguidas - 1)
        return max(0.0, chance)

    def chance_esquiva(self):
        if self.postura == "esquivar":
            return self.chance_esquiva_ativa(self.esquivas_seguidas)
        return self.esquiva

    def receber_ataque(self, dano, so_esquiva_ativa=False):
        """Resolve esquiva e bloqueio. Retorna (dano_recebido, reacao).

        so_esquiva_ativa=True: golpes que a esquiva passiva não pega,
        só quem escolheu esquivar naquele turno tem chance de desviar.
        """
        pode_esquivar = not so_esquiva_ativa or self.postura == "esquivar"
        if pode_esquivar and random.random() < self.chance_esquiva():
            return 0, "esquivou"
        reacao = None
        if self.postura == "bloquear":
            dano = max(1, round(dano * (1 - self.reducao_bloqueio)))
            reacao = "bloqueou"
        self.receber_dano(dano)
        return dano, reacao

    def receber_dano(self, dano):
        self.vida = max(0, self.vida - dano)

    def curar(self, valor):
        antes = self.vida
        self.vida = min(self.vida_max, self.vida + valor)
        return self.vida - antes               # quanto curou de verdade

    def barra_de_vida(self, tamanho=20):
        cheio = round(self.vida / self.vida_max * tamanho)
        return f"[{'#' * cheio}{'-' * (tamanho - cheio)}] {self.vida}/{self.vida_max}"


class Heroi(Personagem):
    """Base dos heróis. Cada subclasse define sua habilidade especial."""

    # Atributos de CLASSE: valem para todos os objetos e cada subclasse sobrescreve
    nome_habilidade = "?"
    custo_habilidade = 0
    descricao = ""

    def __init__(self, nome, vida_max, ataque, defesa, energia_max):
        super().__init__(nome, vida_max, ataque, defesa)
        self.energia_max = energia_max
        self.energia = energia_max
        self.nivel = 1
        self.xp = 0
        self.ouro = 0
        self.inventario = {"pocao": 2}

    def xp_para_subir(self):
        return self.nivel * 15

    def energia_por_turno(self):
        return 2 + (self.nivel - 1)            # 2 no nível 1, +1 por nível

    def ganhar_xp(self, quantidade):
        self.xp += quantidade
        # while e não if: dá pra subir mais de um nível de uma vez
        while self.xp >= self.xp_para_subir():
            self.xp -= self.xp_para_subir()
            self.subir_nivel()

    def subir_nivel(self):
        self.nivel += 1
        self.vida_max += 8
        self.ataque += 2
        self.defesa += 1
        self.energia_max += 3
        self.vida = self.vida_max
        self.energia = self.energia_max
        print(f"\n  *** {self.nome} subiu para o nível {self.nivel}! ***")
        print("  Vida +8, Ataque +2, Defesa +1, Energia +3, Energia por turno +1. "
              "Vida e energia restauradas!")

    def recuperar_energia(self, valor):
        self.energia = min(self.energia_max, self.energia + valor)

    def preparar_para_combate(self):
        # Zera o que vale só durante uma luta. Subclasses podem estender (super()).
        self.postura = None
        self.esquivas_seguidas = 0

    def info_habilidade(self):
        # Texto extra no menu de combate. Por padrão nada; o Ladino mostra o crítico.
        return ""

    def apos_habilidade(self, acertou):
        # Chamado depois que o golpe da habilidade foi resolvido (o alvo pode ter
        # esquivado). Por padrão não faz nada; o Ladino usa para o foco.
        pass

    def usar_habilidade(self, alvo):
        # Cada subclasse sobrescreve: devolve (dano, texto) sem aplicar o dano,
        # porque o alvo ainda pode esquivar ou bloquear.
        raise NotImplementedError

    def mostrar_status(self):
        print(f"\n  {self.nome}, o {type(self).__name__} (nível {self.nivel})")
        print(f"  Vida:    {self.barra_de_vida()}")
        print(f"  Energia: {self.energia}/{self.energia_max} (+{self.energia_por_turno()} por turno)")
        print(f"  Ataque: {self.ataque} | Defesa: {self.defesa}")
        print(f"  Esquiva: {self.esquiva:.0%} passiva, {self.chance_esquiva_ativa(1):.0%} ao esquivar "
              f"| Bloqueio: reduz {self.reducao_bloqueio:.0%} do dano")
        print(f"  XP: {self.xp}/{self.xp_para_subir()} | Ouro: {self.ouro}")
        print(f"  Habilidade: {self.nome_habilidade} ({self.custo_habilidade} energia)")


class Guerreiro(Heroi):
    nome_habilidade = "Golpe Poderoso"
    custo_habilidade = 9
    esquiva = 0.08
    reducao_bloqueio = 0.55
    descricao = "Muita vida e defesa, bloqueio forte. Habilidade: golpe com dano dobrado."

    def __init__(self, nome):
        super().__init__(nome, vida_max=45, ataque=8, defesa=3, energia_max=15)

    def usar_habilidade(self, alvo):
        dano = self.calcular_dano(alvo, multiplicador=2)
        return dano, f"{self.nome} gira a arma com toda a força!"


class Mago(Heroi):
    nome_habilidade = "Bola de Fogo"
    custo_habilidade = 10
    esquiva = 0.15
    reducao_bloqueio = 0.50       # barreira mágica
    descricao = "Frágil, mas com magia poderosa. Habilidade: dano mágico que ignora defesa."

    PODER_INICIAL = 20
    PODER_POR_NIVEL = 3

    def __init__(self, nome):
        super().__init__(nome, vida_max=36, ataque=6, defesa=1, energia_max=30)
        # Atributo que SÓ o Mago tem: o dano mágico. Cresce com o nível,
        # mas a espada (que aumenta o ataque físico) não mexe nele.
        self.poder = self.PODER_INICIAL

    def subir_nivel(self):
        super().subir_nivel()                  # faz tudo que o Heroi já faz...
        self.poder += self.PODER_POR_NIVEL     # ...e acrescenta o que é só do Mago
        print(f"  Poder mágico +{self.PODER_POR_NIVEL}!")

    def mostrar_status(self):
        super().mostrar_status()
        print(f"  Poder mágico: {self.poder}")

    def usar_habilidade(self, alvo):
        # Dano mágico: usa o poder, não o ataque, e ignora a defesa do alvo
        dano = max(1, self.poder + random.randint(-2, 2))
        return dano, f"Uma bola de fogo voa em direção a {alvo.nome}!"


class Ladino(Heroi):
    nome_habilidade = "Ataque Furtivo"
    custo_habilidade = 6
    esquiva = 0.33
    reducao_bloqueio = 0.30
    descricao = ("Ágil, ótimo em esquivar. Habilidade: chance de crítico (2,5x), "
                 "que aumenta a cada tentativa sem crítico.")

    CHANCE_CRITICO = 0.50
    BONUS_FOCO = 0.25          # cada furtivo sem crítico aumenta a chance do próximo
    MULT_CRITICO = 2.5

    def __init__(self, nome):
        super().__init__(nome, vida_max=38, ataque=7, defesa=2, energia_max=20)
        self.foco = 0          # quantos furtivos seguidos sem crítico

    def chance_critico(self):
        return min(1.0, self.CHANCE_CRITICO + self.BONUS_FOCO * self.foco)

    def preparar_para_combate(self):
        super().preparar_para_combate()
        self.foco = 0

    def info_habilidade(self):
        return f", {self.chance_critico():.0%} crítico"

    def mostrar_status(self):
        super().mostrar_status()
        print(f"  Crítico do Ataque Furtivo: {self.chance_critico():.0%} "
              f"(+{self.BONUS_FOCO:.0%} a cada tentativa sem crítico)")

    def usar_habilidade(self, alvo):
        # Aqui só decidimos SE foi crítico. O foco é atualizado em apos_habilidade,
        # porque ainda não sabemos se o alvo vai esquivar.
        self.ultimo_foi_critico = random.random() < self.chance_critico()
        if self.ultimo_foi_critico:
            dano = self.calcular_dano(alvo, multiplicador=self.MULT_CRITICO, ignora_defesa=True)
            return dano, f"{self.nome} acha um ponto fraco! CRÍTICO!"
        dano = self.calcular_dano(alvo)
        return dano, f"{alvo.nome} percebe o movimento a tempo."

    def apos_habilidade(self, acertou):
        if self.ultimo_foi_critico:
            if acertou:
                self.foco = 0                  # crítico que acertou: foco zera
            else:
                print(f"  O crítico não conectou, mas seu foco continua: "
                      f"próximo crítico {self.chance_critico():.0%}.")
        else:
            self.foco += 1
            print(f"  Foco: próximo crítico {self.chance_critico():.0%}.")


# Dicionário de classes: liga o nome (texto) à classe de verdade.
# Usado na criação do personagem e para carregar o save.
CLASSES = {"Guerreiro": Guerreiro, "Mago": Mago, "Ladino": Ladino}


class Inimigo(Personagem):
    def __init__(self, nome, vida, ataque, defesa, xp, ouro, chefe=False,
                 esquiva=0.0, reducao_bloqueio=0.0):
        super().__init__(nome, vida, ataque, defesa)
        self.xp = xp
        self.ouro = ouro
        self.chefe = chefe
        # atributo do OBJETO: tem prioridade sobre o atributo da classe Personagem
        self.esquiva = esquiva
        self.reducao_bloqueio = reducao_bloqueio

    def decidir_se_defende(self):
        # Inimigos que sabem bloquear se protegem às vezes quando estão fracos
        return (not self.chefe and self.reducao_bloqueio > 0
                and self.vida < self.vida_max * 0.35 and random.random() < 0.4)


# Os dados de cada inimigo ficam num dict, e o ** "abre" esse dict como
# argumentos nomeados: Inimigo(**INIMIGOS["rato"]) é o mesmo que
# Inimigo(nome="Rato Gigante", vida=14, ataque=5, ...)
INIMIGOS = {
    "rato":      {"nome": "Rato Gigante", "vida": 14, "ataque": 5,  "defesa": 0, "xp": 8,  "ouro": 3,
                  "esquiva": 0.25},
    "esqueleto": {"nome": "Esqueleto",    "vida": 22, "ataque": 8,  "defesa": 2, "xp": 14, "ouro": 8,
                  "esquiva": 0.05, "reducao_bloqueio": 0.5},
    "goblin":    {"nome": "Goblin",       "vida": 26, "ataque": 9,  "defesa": 2, "xp": 16, "ouro": 12,
                  "esquiva": 0.20, "reducao_bloqueio": 0.3},
    "zumbi":     {"nome": "Zumbi",        "vida": 34, "ataque": 9,  "defesa": 1, "xp": 18, "ouro": 6},
    "lich":      {"nome": "O Lich",       "vida": 100, "ataque": 15, "defesa": 5, "xp": 100, "ouro": 100,
                  "chefe": True, "esquiva": 0.10},
}


def criar_inimigo(chave):
    return Inimigo(**INIMIGOS[chave])


# ============================================================================
#  ITENS
# ============================================================================

ITENS = {
    "pocao":  {"nome": "Poção de Vida",  "descricao": f"Recupera {CURA_POCAO} de vida."},
    "espada": {"nome": "Espada Afiada",  "descricao": "Ataque +3.", "bonus": ("ataque", 3)},
    "escudo": {"nome": "Escudo de Ferro", "descricao": "Defesa +2.", "bonus": ("defesa", 2)},
    "chave":  {"nome": "Chave de Osso",  "descricao": "Abre a porta da sala do trono."},
}


def pegar_item(heroi, chave):
    item = ITENS[chave]
    heroi.inventario[chave] = heroi.inventario.get(chave, 0) + 1
    print(f"  Você pegou: {item['nome']}. {item['descricao']}")

    # Equipamentos dão bônus na hora de pegar
    if "bonus" in item:
        atributo, valor = item["bonus"]                       # desempacota a tupla
        setattr(heroi, atributo, getattr(heroi, atributo) + valor)
        # getattr/setattr leem e alteram um atributo pelo NOME em texto:
        # setattr(heroi, "ataque", x) é o mesmo que heroi.ataque = x


def usar_pocao(heroi):
    if heroi.inventario.get("pocao", 0) == 0:
        print("  Você não tem poções.")
        return False
    if heroi.vida == heroi.vida_max:
        print("  Sua vida já está cheia.")
        return False
    heroi.inventario["pocao"] -= 1
    curou = heroi.curar(CURA_POCAO)
    print(f"  Você bebe a poção e recupera {curou} de vida. Vida: {heroi.vida}/{heroi.vida_max}")
    return True


def mostrar_inventario(heroi):
    print("\n  Inventário:")
    itens = {k: v for k, v in heroi.inventario.items() if v > 0}
    if not itens:
        print("    (vazio)")
    for chave, quantidade in itens.items():
        print(f"    {ITENS[chave]['nome']} x{quantidade} - {ITENS[chave]['descricao']}")
    print(f"  Ouro: {heroi.ouro}")


# ============================================================================
#  MAPA
# ============================================================================
#
#               [Trono]
#                  |
#   [Cripta]   [Corredor]--[Fonte]
#      |           |
# [Biblioteca]--[Salão]--[Arsenal]
#                  |
#              [Entrada]

MAPA_DESENHO = r"""
                [Trono]
                   |
    [Cripta]   [Corredor]--[Fonte]
       |           |
  [Biblioteca]--[Salão]--[Arsenal]
                   |
               [Entrada]
"""


def criar_mapa():
    # Uma função que cria o mapa do zero (para cada jogo novo).
    # Inimigos derrotados e itens pegos viram None, e o mapa vai junto no save.
    return {
        "entrada": {
            "nome": "Entrada da Masmorra",
            "descricao": "Degraus de pedra descem para a escuridão. Um velho mercador "
                         "se aquece numa pequena fogueira ao lado da porta.",
            "saidas": {"norte": "salao"},
            "inimigo": None, "item": None, "mercador": True,
        },
        "salao": {
            "nome": "Grande Salão",
            "descricao": "Colunas rachadas sustentam um teto alto. Algo se mexe entre os "
                         "escombros. Passagens levam para todos os lados.",
            "saidas": {"sul": "entrada", "norte": "corredor", "leste": "arsenal", "oeste": "biblioteca"},
            "inimigo": "rato", "item": None,
        },
        "arsenal": {
            "nome": "Arsenal Abandonado",
            "descricao": "Suportes de armas enferrujadas cobrem as paredes. Ossos estalam "
                         "no canto da sala.",
            "saidas": {"oeste": "salao"},
            "inimigo": "esqueleto", "item": "espada",
        },
        "biblioteca": {
            "nome": "Biblioteca Mofada",
            "descricao": "Estantes caídas e livros apodrecendo. Um cheiro de ervas vem de "
                         "uma mesa de alquimia. Uma escada desce para o norte.",
            "saidas": {"leste": "salao", "norte": "cripta"},
            "inimigo": None, "item": "pocao",
        },
        "cripta": {
            "nome": "Cripta",
            "descricao": "Caixões abertos. Um gemido ecoa, e algo se levanta de um deles.",
            "saidas": {"sul": "biblioteca"},
            "inimigo": "zumbi", "item": "chave",
        },
        "corredor": {
            "nome": "Corredor das Tochas",
            "descricao": "Tochas azuladas iluminam uma porta enorme ao norte, decorada com "
                         "caveiras. Há um brilho suave a leste.",
            "saidas": {"sul": "salao", "norte": "trono", "leste": "fonte"},
            "inimigo": "goblin", "item": "escudo",
        },
        "fonte": {
            "nome": "Fonte Encantada",
            "descricao": "Uma fonte de água prateada brilha no centro da sala. "
                         "Digite 'beber' para se recuperar.",
            "saidas": {"oeste": "corredor"},
            "inimigo": None, "item": None, "fonte": True,
        },
        "trono": {
            "nome": "Sala do Trono",
            "descricao": "Num trono de ossos, uma figura esquelética de coroa abre os olhos "
                         "brilhantes. 'Mais um herói para minha coleção...'",
            "saidas": {"sul": "corredor"},
            "inimigo": "lich", "item": None, "trancada": True,
        },
    }


# ============================================================================
#  COMBATE
# ============================================================================

MULT_RAIO_SOMBRIO = 2.0   # força do ataque especial do chefe
LIMIAR_DICA_ESQUIVA = 0.6 # a partir dessa chance de esquiva ativa, a dica sugere desviar
CONTRA_ATAQUE = True      # esquiva ATIVA bem-sucedida devolve um ataque normal


def resolver_golpe(alvo, dano, texto, so_esquiva_ativa=False, atacante=None):
    """Aplica um golpe no alvo (que pode esquivar/bloquear) e narra o resultado."""
    postura_do_alvo = alvo.postura
    recebido, reacao = alvo.receber_ataque(dano, so_esquiva_ativa)
    if reacao == "esquivou":
        msg = f"  {texto} Mas {alvo.nome} se esquiva!"
    elif reacao == "bloqueou":
        msg = f"  {texto} {alvo.nome} bloqueia e recebe só {recebido} de dano."
    else:
        msg = f"  {texto} {recebido} de dano!"
    if isinstance(alvo, Heroi):
        msg += f" Vida: {alvo.vida}/{alvo.vida_max}"
    print(msg)

    # Contra-ataque: só quando o alvo esquivou DE PROPÓSITO (não vale a passiva)
    if CONTRA_ATAQUE and reacao == "esquivou" and postura_do_alvo == "esquivar" and atacante:
        contra = alvo.calcular_dano(atacante)
        resolver_golpe(atacante, contra, f"{alvo.nome} aproveita a abertura e contra-ataca!")
    return reacao


def dica_raio(heroi):
    # Decide pelo ATRIBUTO, não pelo nome da classe: uma classe nova ou um item
    # que aumente a esquiva já muda a dica sem precisar mexer aqui.
    if heroi.chance_esquiva_ativa(1) >= LIMIAR_DICA_ESQUIVA:
        return "Seus instintos dizem que, atento, dá pra sair do caminho."
    return "Melhor estar com a guarda erguida."


def vitoria(heroi, inimigo):
    print(f"\n  {inimigo.nome} foi derrotado! +{inimigo.xp} XP, +{inimigo.ouro} de ouro.")
    heroi.ouro += inimigo.ouro
    heroi.ganhar_xp(inimigo.xp)
    heroi.postura = None
    return "venceu"


def combate(heroi, inimigo):
    """Retorna 'venceu', 'fugiu' ou 'morreu'."""
    print(f"\n  !!! {inimigo.nome} ataca! !!!")
    heroi.preparar_para_combate()
    turno_inimigo = 0          # só conta quando o inimigo age (marca o ritmo do Raio Sombrio)

    while True:
        proxima_esquiva = heroi.chance_esquiva_ativa(heroi.esquivas_seguidas + 1)
        print(f"\n  {heroi.nome:<14} {heroi.barra_de_vida()}  Energia: {heroi.energia}/{heroi.energia_max}")
        print(f"  {inimigo.nome:<14} {inimigo.barra_de_vida()}")
        print(f"  1 - Atacar   2 - {heroi.nome_habilidade} ({heroi.custo_habilidade} energia"
              f"{heroi.info_habilidade()})   "
              f"3 - Poção ({heroi.inventario.get('pocao', 0)})")
        print(f"  4 - Esquivar ({proxima_esquiva:.0%})   "
              f"5 - Bloquear (-{heroi.reducao_bloqueio:.0%} de dano)   6 - Fugir")
        acao = input("  Ação: ").strip()

        # ---- turno do herói ----
        if acao == "1":
            dano = heroi.calcular_dano(inimigo)
            resolver_golpe(inimigo, dano, f"Você ataca {inimigo.nome}.")
        elif acao == "2":
            if heroi.energia < heroi.custo_habilidade:
                print("  Energia insuficiente!")
                continue                         # não gasta o turno
            heroi.energia -= heroi.custo_habilidade
            dano, texto = heroi.usar_habilidade(inimigo)   # polimorfismo: cada classe faz a sua
            reacao = resolver_golpe(inimigo, dano, texto)
            heroi.apos_habilidade(acertou=(reacao != "esquivou"))
        elif acao == "3":
            if not usar_pocao(heroi):
                continue
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
            if random.random() < 0.5:
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

        if not inimigo.esta_vivo():
            return vitoria(heroi, inimigo)

        # ---- turno do inimigo ----
        turno_inimigo += 1
        inimigo.postura = None                   # a guarda do turno anterior acabou

        if inimigo.chefe and turno_inimigo % 3 == 0:
            # Ataque especial: ignora a defesa, e a esquiva passiva não funciona
            # contra ele. Só bloqueando ou esquivando de propósito.
            dano = inimigo.calcular_dano(heroi, multiplicador=MULT_RAIO_SOMBRIO, ignora_defesa=True)
            resolver_golpe(heroi, dano, f"{inimigo.nome} conjura um RAIO SOMBRIO!",
                           so_esquiva_ativa=True, atacante=inimigo)
        elif inimigo.decidir_se_defende():
            inimigo.postura = "bloquear"
            print(f"  {inimigo.nome} recua e ergue a guarda.")
        else:
            dano = inimigo.calcular_dano(heroi)
            resolver_golpe(heroi, dano, f"{inimigo.nome} ataca.", atacante=inimigo)

        if inimigo.chefe and turno_inimigo % 3 == 2:
            print(f"  {inimigo.nome} começa a reunir energia sombria... {dica_raio(heroi)}")

        if not heroi.esta_vivo():
            heroi.postura = None
            return "morreu"
        if not inimigo.esta_vivo():              # pode morrer no contra-ataque
            return vitoria(heroi, inimigo)

        heroi.recuperar_energia(heroi.energia_por_turno())


# ============================================================================
#  SALVAR E CARREGAR
# ============================================================================

def salvar(heroi, sala_atual, mapa):
    dados = {
        "classe": type(heroi).__name__,   # "Guerreiro", "Mago" ou "Ladino"
        "heroi": vars(heroi),             # vars() devolve os atributos do objeto como dict
        "sala": sala_atual,
        "mapa": mapa,
    }
    with open(ARQUIVO_SAVE, "w", encoding="utf-8") as arquivo:
        json.dump(dados, arquivo, indent=2, ensure_ascii=False)
    print("  Jogo salvo!")


def carregar():
    with open(ARQUIVO_SAVE, "r", encoding="utf-8") as arquivo:
        dados = json.load(arquivo)
    classe = CLASSES[dados["classe"]]           # texto -> classe de verdade
    heroi = classe(dados["heroi"]["nome"])      # cria o herói...
    vars(heroi).update(dados["heroi"])          # ...e sobrescreve com os dados salvos
    return heroi, dados["sala"], dados["mapa"]


# ============================================================================
#  EXPLORAÇÃO
# ============================================================================

DIRECOES = {"n": "norte", "s": "sul", "l": "leste", "o": "oeste",
            "norte": "norte", "sul": "sul", "leste": "leste", "oeste": "oeste"}

AJUDA = """
  Comandos:
    norte, sul, leste, oeste (ou n, s, l, o)  - andar
    olhar      - descrever a sala de novo
    pegar      - pegar o item da sala
    status     - ver seu personagem
    inventario - ver seus itens
    pocao      - beber uma poção de vida
    mapa       - ver o mapa da masmorra
    comprar    - comprar poção (onde houver mercador)
    beber      - beber da fonte (na Fonte Encantada)
    salvar     - salvar o jogo
    sair       - sair do jogo
"""


def descrever_sala(sala):
    print(f"\n=== {sala['nome']} ===")
    print(sala["descricao"])
    if sala["item"]:
        print(f"Você vê algo no chão: {ITENS[sala['item']]['nome']}.")
    saidas = ", ".join(sala["saidas"])
    print(f"Saídas: {saidas}")


def entrar_na_sala(heroi, mapa, sala_id):
    """Descreve a sala e dispara o combate se tiver inimigo.
    Retorna o resultado do combate, ou None se não houve luta."""
    sala = mapa[sala_id]
    descrever_sala(sala)

    if sala["inimigo"]:
        inimigo = criar_inimigo(sala["inimigo"])
        resultado = combate(heroi, inimigo)
        if resultado == "venceu":
            sala["inimigo"] = None               # não aparece de novo
        return resultado
    return None


def tentar_andar(heroi, mapa, sala_atual, direcao):
    """Retorna o id da próxima sala, ou None se não der pra ir."""
    saidas = mapa[sala_atual]["saidas"]
    if direcao not in saidas:
        print("  Não há passagem nessa direção.")
        return None

    destino = saidas[direcao]
    if mapa[destino].get("trancada"):
        if heroi.inventario.get("chave", 0) > 0:
            print("  Você usa a Chave de Osso. A porta range e se abre...")
            heroi.inventario["chave"] -= 1
            mapa[destino]["trancada"] = False
        else:
            print("  A porta está trancada. Parece precisar de uma chave feita de osso.")
            return None
    return destino


def jogar(heroi, sala_atual, mapa):
    resultado = entrar_na_sala(heroi, mapa, sala_atual)
    sala_anterior = sala_atual

    while True:
        # ---- checa o que aconteceu ao entrar na sala ----
        if resultado == "morreu":
            print(f"\n  {heroi.nome} caiu na escuridão da masmorra...")
            print("  ========== FIM DE JOGO ==========")
            return
        if resultado == "fugiu":
            print("  Você volta correndo para a sala anterior.")
            sala_atual = sala_anterior
            descrever_sala(mapa[sala_atual])
        if resultado == "venceu" and sala_atual == "trono":
            print("\n  O Lich se desfaz em pó, e a coroa cai aos seus pés.")
            print("  A maldição da masmorra foi quebrada!")
            print(f"\n  ===== VITÓRIA! {heroi.nome} chegou ao nível {heroi.nivel} "
                  f"com {heroi.ouro} de ouro. =====")
            return
        resultado = None

        # ---- lê um comando ----
        comando = input("\n> ").strip().lower()
        sala = mapa[sala_atual]

        if comando in DIRECOES:
            destino = tentar_andar(heroi, mapa, sala_atual, DIRECOES[comando])
            if destino:
                sala_anterior, sala_atual = sala_atual, destino
                resultado = entrar_na_sala(heroi, mapa, sala_atual)
        elif comando == "olhar":
            descrever_sala(sala)
        elif comando == "pegar":
            if sala["item"]:
                pegar_item(heroi, sala["item"])
                sala["item"] = None
            else:
                print("  Não há nada para pegar aqui.")
        elif comando == "status":
            heroi.mostrar_status()
        elif comando in ("inventario", "inventário", "i"):
            mostrar_inventario(heroi)
        elif comando in ("pocao", "poção"):
            usar_pocao(heroi)
        elif comando == "mapa":
            print(MAPA_DESENHO)
            print(f"  Você está em: {sala['nome']}")
        elif comando == "comprar":
            if not sala.get("mercador"):
                print("  Não há ninguém vendendo nada aqui.")
            elif heroi.ouro < PRECO_POCAO:
                print(f"  'Uma poção custa {PRECO_POCAO} de ouro, aventureiro. Volte quando tiver.'")
            else:
                heroi.ouro -= PRECO_POCAO
                heroi.inventario["pocao"] = heroi.inventario.get("pocao", 0) + 1
                print(f"  Você compra uma poção. Ouro restante: {heroi.ouro}")
        elif comando == "beber":
            if sala.get("fonte"):
                heroi.vida = heroi.vida_max
                heroi.energia = heroi.energia_max
                print("  A água gelada percorre seu corpo. Vida e energia restauradas!")
            else:
                print("  Não há nada para beber aqui.")
        elif comando == "salvar":
            salvar(heroi, sala_atual, mapa)
        elif comando == "ajuda":
            print(AJUDA)
        elif comando == "sair":
            if input("  Salvar antes de sair? (s/n) ").strip().lower() == "s":
                salvar(heroi, sala_atual, mapa)
            print("  Até a próxima!")
            return
        elif comando == "":
            continue
        else:
            print("  Comando desconhecido. Digite 'ajuda' para ver os comandos.")


# ============================================================================
#  INÍCIO
# ============================================================================

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
        if escolha in ("1", "2", "3"):
            classe = CLASSES[nomes_classes[int(escolha) - 1]]
            return classe(nome)
        print("Escolha 1, 2 ou 3.")


TITULO = r"""
  ================================================
       A   M A S M O R R A   D O   L I C H
  ================================================
"""


def main():
    print(TITULO)
    tem_save = os.path.exists(ARQUIVO_SAVE)
    print("  1 - Novo jogo")
    if tem_save:
        print("  2 - Continuar jogo salvo")
    print("  0 - Sair")

    while True:
        opcao = input("> ").strip()
        if opcao == "1":
            heroi = criar_personagem()
            print(f"\n{heroi.nome}, o {type(heroi).__name__}, desce os degraus da masmorra.")
            print("Dizem que um Lich governa este lugar. Digite 'ajuda' para ver os comandos.")
            jogar(heroi, "entrada", criar_mapa())
            return
        if opcao == "2" and tem_save:
            try:
                heroi, sala, mapa = carregar()
            except (json.JSONDecodeError, KeyError):
                print("  O save está corrompido. Comece um jogo novo.")
                continue
            print(f"\n  Bem-vindo de volta, {heroi.nome}!")
            jogar(heroi, sala, mapa)
            return
        if opcao == "0":
            return
        print("  Opção inválida.")


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print("\n  Até a próxima!")
