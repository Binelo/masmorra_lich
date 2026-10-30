# ============================================================================
#  personagens.py - quem luta: heróis e inimigos
# ============================================================================
#  A base Personagem (vida, ataque, esquiva, bloqueio, efeitos) e os heróis.
#  Os inimigos ficam em inimigos.py.
#
#  Para criar uma classe de herói nova: faça uma subclasse de Heroi,
#  implemente usar_habilidade() e adicione no dicionário CLASSES.
# ============================================================================

import random


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
        self.efeitos = {}             # ex.: {"veneno": 3, "preso": 1} -> efeito: turnos restantes
        self.dano_continuo = {}       # dano por ação de cada efeito: {"veneno": 2, "queimadura": 3}
        self.mult_exposto = 1.5       # quanto dano a mais recebe quando está "vulneravel"
        self.notas = []               # frases extras sobre o último golpe recebido

    def esta_vivo(self):
        return self.vida > 0

    def calcular_dano(self, alvo, multiplicador=1, ignora_defesa=False):
        # Um pouco de sorte em cada golpe: ataque de -2 a +2
        base = (self.ataque + random.randint(-2, 2)) * multiplicador
        if getattr(self, "furia", 0) and self.vida < self.vida_max / 2:
            base *= 1 + self.furia            # Braçadeira da Fúria: mais forte quando ferido
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

    def receber_ataque(self, dano, so_esquiva_ativa=False, inesquivavel=False,
                       alcance=1, elemento=None, fisico=False):
        """Resolve esquiva, vulnerabilidade e bloqueio. Retorna (dano_recebido, reacao).

        so_esquiva_ativa: a esquiva passiva não pega, só quem escolheu esquivar.
        inesquivavel:     ninguém desvia (ex.: explosão de bomba).
        alcance:          quantos alvos o golpe atinge (só importa para enxames).
        elemento:         ex.: "fogo" (só importa para quem reage a ele, como o Troll).
        fisico:           True para golpes com a arma (importa para quem voa, como a dragoa).
        """
        pode_esquivar = not inesquivavel and (not so_esquiva_ativa or self.postura == "esquivar")
        if pode_esquivar and random.random() < self.chance_esquiva():
            return 0, "esquivou"
        if self.efeitos.get("vulneravel"):
            dano = round(dano * self.mult_exposto)
            self.notas.append(f"{self.nome} está exposto e sofre mais!")
        reacao = None
        if self.postura == "bloquear":
            dano = max(1, round(dano * (1 - self.reducao_bloqueio)))
            reacao = "bloqueou"
        self.receber_dano(dano)
        return dano, reacao

    def texto_dano(self, recebido):
        # Como o dano aparece na tela. O enxame sobrescreve (mostra morcegos caindo).
        return f"{recebido} de dano!"

    def passar_turno_efeitos(self):
        """Diminui em 1 a duração de cada efeito e remove os que acabaram."""
        for efeito in list(self.efeitos):          # list(): não dá pra apagar de um dict enquanto percorre
            self.efeitos[efeito] -= 1
            if self.efeitos[efeito] <= 0:
                del self.efeitos[efeito]

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

    ESPACOS = ("arma", "escudo", "armadura", "acessorio", "acessorio_2")
    alcance_habilidade = 1      # quantos alvos a habilidade atinge (importa contra enxames)
    elemento_habilidade = None  # ex.: "fogo"
    atordoar_habilidade = 0.0   # chance de a habilidade atordoar (chefes resistem)
    acoes_extras_habilidade = 0 # > 0: a habilidade não ataca, dá ações extras (Surto de Ação)

    def __init__(self, nome, vida_max, ataque, defesa, energia_max):
        super().__init__(nome, vida_max, ataque, defesa)
        self.energia_max = energia_max
        self.energia = energia_max
        self.nivel = 1
        self.xp = 0
        self.ouro = 0
        self.inventario = {"pocao": 2}
        self.equipamento = {espaco: None for espaco in self.ESPACOS}   # dict comprehension
        self.arma_envenenada = False   # Glândula de Veneno (recompensa da aranha)
        self.cura_defensiva = 0        # Coração de Troll: vida ao esquivar/bloquear com sucesso
        self.curou_no_turno = False
        self.revivido = False          # já voltou da morte com o Filactério nesta partida?
        self.abates = {}               # inimigos derrotados nesta partida: {nome: quantos}
        self.xp_total = 0              # todo o XP ganho na partida (vira Ecos no fim)
        self.andares_concluidos = []
        self.ultimo_inimigo = None     # com quem lutou por último (quem te matou, se morrer)
        # Atributos que só vêm de equipamento (via "bonus" no itens.json):
        self.roubo_vida = 0.0          # fração do dano causado que volta como vida
        self.chance_atordoar = 0.0     # chance de o golpe fazer o inimigo perder o turno
        self.espinhos = 0              # dano devolvido a quem te acerta
        self.resistencia_fogo = 0.0    # fração do dano de fogo ignorada (0.4 = -40%)
        self.furia = 0.0               # dano extra dos golpes com menos de metade da vida

    def xp_para_subir(self):
        return self.nivel * 15

    def energia_por_turno(self):
        return 2 + (self.nivel - 1)            # 2 no nível 1, +1 por nível

    def ganhar_xp(self, quantidade):
        self.xp += quantidade
        self.xp_total += quantidade
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
        self.efeitos = {}
        self.notas = []

    def info_habilidade(self):
        # Texto extra no menu de combate. Por padrão nada; o Ladino mostra o crítico.
        return ""

    def receber_ataque(self, dano, **opcoes):
        """Igual ao de Personagem, mais a cura defensiva (Coração de Troll):
        esquivar ou bloquear DE PROPÓSITO com sucesso cura um pouco, uma vez por turno."""
        postura = self.postura
        if opcoes.get("elemento") == "fogo" and self.resistencia_fogo:
            dano = max(1, round(dano * (1 - self.resistencia_fogo)))
            self.notas.append("Sua proteção contra fogo absorve parte do calor.")
        recebido, reacao = super().receber_ataque(dano, **opcoes)
        defendeu = (postura == "esquivar" and reacao == "esquivou") or \
                   (postura == "bloquear" and reacao == "bloqueou")
        if self.cura_defensiva and defendeu and not self.curou_no_turno and self.esta_vivo():
            self.curou_no_turno = True
            curou = self.curar(self.cura_defensiva)
            if curou:
                self.notas.append(f"Sua carne se fecha sozinha: +{curou} de vida.")
        return recebido, reacao

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
        if self.arma_envenenada:
            print("  Arma envenenada: seus golpes envenenam (mortos-vivos e enxames são imunes)")
        if self.cura_defensiva:
            print(f"  Cura defensiva: +{self.cura_defensiva} de vida ao esquivar/bloquear com sucesso")
        if self.roubo_vida:
            print(f"  Roubo de vida: {self.roubo_vida:.0%} do dano dos seus golpes")
        if self.chance_atordoar:
            print(f"  Chance de atordoar: {self.chance_atordoar:.0%} (chefes e mini-chefes resistem)")
        if self.espinhos:
            print(f"  Espinhos: quem te acerta toma {self.espinhos} de dano")
        if self.resistencia_fogo:
            print(f"  Resistência a fogo: {self.resistencia_fogo:.0%}")
        if self.furia:
            print(f"  Fúria: +{self.furia:.0%} de dano com menos de metade da vida")


class Guerreiro(Heroi):
    nome_habilidade = "Surto de Ação"
    custo_habilidade = 10
    acoes_extras_habilidade = 2   # a habilidade não ataca: dá 2 ações neste turno
    esquiva = 0.08
    reducao_bloqueio = 0.55
    descricao = ("Muita vida e defesa, bloqueio forte. Habilidade: Surto de Ação, "
                 "age duas vezes no mesmo turno.")

    def __init__(self, nome):
        super().__init__(nome, vida_max=45, ataque=8, defesa=3, energia_max=15)

    def info_habilidade(self):
        return f", {self.acoes_extras_habilidade} ações"


class Mago(Heroi):
    nome_habilidade = "Bola de Fogo"
    custo_habilidade = 12
    alcance_habilidade = 99       # explosão: atinge todos os alvos
    elemento_habilidade = "fogo"
    esquiva = 0.15
    reducao_bloqueio = 0.50       # barreira mágica
    descricao = "Frágil, mas com magia poderosa. Habilidade: dano mágico que ignora defesa."

    PODER_INICIAL = 18
    PODER_POR_NIVEL = 3

    def __init__(self, nome):
        super().__init__(nome, vida_max=40, ataque=6, defesa=1, energia_max=30)
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
    custo_habilidade = 10
    esquiva = 0.30
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
