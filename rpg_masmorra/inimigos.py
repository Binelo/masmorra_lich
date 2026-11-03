# ============================================================================
#  inimigos.py - os monstros e como cada um age no seu turno
# ============================================================================
#  Os NÚMEROS ficam em dados/inimigos.json. O campo "tipo" escolhe a classe:
#    (sem tipo)  Inimigo   - ataca; pode ter um "especial" (como o Lich)
#    "enxame"    Enxame    - vários bichos fracos; ataques em área matam vários
#    "aranha"    Aranha    - mordida venenosa (dano_veneno por ação, no JSON) e teia que prende
#    "troll"     Troll     - alterna atacar e regenerar; pancada atordoante avisada;
#                            fogo impede a regeneração
#    "kobolds"   KoboldsArmadilheiros - enxame que arma armadilhas (prendem)
#    "golem"     Golem     - blindado, golpe carregado; golpes fortes racham a armadura
#    "berserker" Berserker - fica mais forte conforme perde vida
#    "capataz"   Capataz   - escudo de torre; fica aberto depois do golpe de martelo
#    "dragao"    Dragao    - chefe em 2 fases: sopro (só bloquear) e voo (mergulho, esquivável)
#
#  Campos genéricos úteis: "elemento_ataque": "fogo", "embosca": true (ataca primeiro),
#  "efeito_ao_acertar": {"efeito": "queimadura", "turnos": 3, "dano": 3}
#
#  Para um comportamento novo: crie uma subclasse de Inimigo, sobrescreva
#  agir() (e o que mais precisar) e registre no dicionário TIPOS lá embaixo.
# ============================================================================

import random

import dados
from golpes import DICA_BLOQUEAR, DICA_ESQUIVAR, bom_de_esquiva, resolver_golpe
from personagens import Personagem


class Inimigo(Personagem):
    def __init__(self, nome, vida, ataque, defesa, xp, ouro, chefe=False,
                 esquiva=0.0, reducao_bloqueio=0.0, especial=None, texto_derrota=None,
                 drop=None, drop_tabela=None, imune_veneno=False, fraquezas=None,
                 elemento_ataque=None, efeito_ao_acertar=None, embosca=False, drops_extras=None,
                 resiste_controle=None):
        super().__init__(nome, vida, ataque, defesa)
        self.xp = xp
        self.ouro = ouro
        self.chefe = chefe
        # atributo do OBJETO: tem prioridade sobre o atributo da classe Personagem
        self.esquiva = esquiva
        self.reducao_bloqueio = reducao_bloqueio
        self.especial = especial            # dict com o ataque especial (ou None)
        self.texto_derrota = texto_derrota  # texto mostrado quando um chefe é derrotado
        self.drop = drop                    # item que ele sempre deixa ao morrer
        self.drop_tabela = drop_tabela      # ...ou UM item sorteado desta tabela do saque.json
        self.imune_veneno = imune_veneno
        self.fraquezas = fraquezas or {}    # ex.: {"fogo": 1.25} -> fogo causa +25%
        self.elemento_ataque = elemento_ataque      # ex.: "fogo" -> o ataque normal é de fogo
        self.efeito_ao_acertar = efeito_ao_acertar  # ex.: {"efeito": "queimadura", "turnos": 3, "dano": 3}
        self.embosca = embosca              # True: ataca primeiro, antes do herói agir
        self.drops_extras = drops_extras or []  # vários itens de uma vez (ex.: o herói caído)
        # Chefes e mini-chefes (quem deixa um item único) não perdem o turno por
        # atordoamento ou congelamento das armas/bombas. Só itens de "congelar" funcionam.
        if resiste_controle is None:
            resiste_controle = chefe or bool(drop)
        self.resiste_controle = resiste_controle

    def receber_ataque(self, dano, so_esquiva_ativa=False, inesquivavel=False,
                       alcance=1, elemento=None, fisico=False):
        multiplicador = self.fraquezas.get(elemento, 1)
        if fisico and multiplicador < 0.5:
            multiplicador = 0.5       # golpe com arma: mesmo imune ao elemento, a lâmina ainda corta
        if multiplicador != 1:
            dano = round(dano * multiplicador)
            if multiplicador == 0:
                self.notas.append(f"{self.nome} é imune a {elemento}!")
            elif multiplicador < 1:
                self.notas.append(f"{self.nome} resiste a {elemento}.")
            else:
                self.notas.append(f"{self.nome} é fraco contra {elemento}!")
        return super().receber_ataque(dano, so_esquiva_ativa, inesquivavel, alcance, elemento, fisico)

    def texto_aparece(self):
        return f"{self.nome} ataca!"

    def decidir_se_defende(self):
        # Inimigos que sabem bloquear se protegem às vezes quando estão fracos
        return (not self.chefe and self.reducao_bloqueio > 0
                and self.vida < self.vida_max * 0.35 and random.random() < 0.4)

    def atacar(self, heroi, texto=None, multiplicador=1):
        dano = self.calcular_dano(heroi, multiplicador=multiplicador)
        reacao = resolver_golpe(heroi, dano, texto or f"{self.nome} ataca.",
                                elemento=self.elemento_ataque, atacante=self)
        if reacao != "esquivou" and self.efeito_ao_acertar and heroi.esta_vivo():
            efeito = self.efeito_ao_acertar
            if efeito["efeito"] not in heroi.efeitos:
                print(f"  {NOMES_AO_SOFRER.get(efeito['efeito'], efeito['efeito'])}")
            heroi.efeitos[efeito["efeito"]] = efeito["turnos"]          # renova, não acumula
            if "dano" in efeito:
                heroi.dano_continuo[efeito["efeito"]] = efeito["dano"]
        return reacao

    def agir(self, heroi, turno):
        """O turno do inimigo. turno = quantas vezes ele já agiu nesta luta."""
        self.postura = None                  # a guarda do turno anterior acabou
        especial = self.especial

        if especial and turno % especial["a_cada"] == 0:
            dano = self.calcular_dano(heroi, multiplicador=especial["multiplicador"],
                                      ignora_defesa=especial.get("ignora_defesa", False))
            resolver_golpe(heroi, dano, f"{self.nome} {especial['texto']}",
                           so_esquiva_ativa=especial.get("so_esquiva_ativa", False),
                           inesquivavel=especial.get("inesquivavel", False), atacante=self)
        elif self.decidir_se_defende():
            self.postura = "bloquear"
            print(f"  {self.nome} recua e ergue a guarda.")
        else:
            self.atacar(heroi)

        # Aviso um turno antes do especial
        if especial and turno % especial["a_cada"] == especial["a_cada"] - 1:
            pode_esquivar = not especial.get("inesquivavel", False)
            dica = DICA_ESQUIVAR if pode_esquivar and bom_de_esquiva(heroi) else DICA_BLOQUEAR
            print(f"  {self.nome} {especial['aviso']} {dica}")


NOMES_AO_SOFRER = {"veneno": "Você foi envenenado!", "queimadura": "Você está pegando fogo!"}


def dica_desviar_ou(heroi, alternativa):
    """Dica para golpes que só a esquiva ativa evita."""
    return DICA_ESQUIVAR if bom_de_esquiva(heroi) else alternativa


class Enxame(Inimigo):
    """Vários bichos fracos tratados como um inimigo só.
    Cada golpe normal derruba um; golpes com alcance maior derrubam vários."""

    def __init__(self, nome, quantidade, vida_cada, nome_singular="bicho", dano_cada=None, **resto):
        super().__init__(nome, vida=quantidade * vida_cada, ataque=resto.pop("ataque", 1), **resto)
        self.dano_cada = dano_cada     # se definido: cada mordida causa esse dano (ignora a defesa)
        self.quantidade = quantidade
        self.vida_cada = vida_cada
        self.nome_singular = nome_singular

    def texto_aparece(self):
        return f"{self.nome} atacam!"

    def vivos(self):
        return -(-self.vida // self.vida_cada)   # divisão arredondando pra cima

    def matar(self, quantos):
        quantos = min(quantos, self.vivos())
        self.vida = (self.vivos() - quantos) * self.vida_cada
        return quantos

    def receber_ataque(self, dano, so_esquiva_ativa=False, inesquivavel=False,
                       alcance=1, elemento=None, fisico=False):
        if not inesquivavel and random.random() < self.esquiva:
            return 0, "esquivou"
        mortos = self.matar(alcance) if dano >= self.vida_cada else 0
        if mortos:
            plural = f"{mortos} {self.nome_singular}s caem" if mortos > 1 else f"1 {self.nome_singular} cai"
            self.notas.append(f"{plural}! Restam {self.vivos()}.")
        return mortos * self.vida_cada, None

    def receber_dano(self, dano):
        # dano sem golpe (ex.: efeitos) derruba um
        if dano > 0:
            self.matar(1)

    def texto_dano(self, recebido):
        return "" if recebido else "Não acerta nenhum."

    def barra_de_vida(self, tamanho=20):
        return f"[{'v ' * self.vivos()}{'. ' * (self.quantidade - self.vivos())}] {self.vivos()}/{self.quantidade} vivos"

    def agir(self, heroi, turno):
        """Cada bicho vivo ataca separado (o herói pode desviar de cada um)."""
        acertos = desvios = dano_total = 0
        contra_atacou = False
        heroi.notas = []
        for _ in range(self.vivos()):
            dano = self.dano_cada if self.dano_cada else self.calcular_dano(heroi)
            postura = heroi.postura
            recebido, reacao = heroi.receber_ataque(dano)
            if reacao == "esquivou":
                desvios += 1
                # contra-ataque do herói derruba um bicho (uma vez por turno)
                if postura == "esquivar" and not contra_atacou and self.matar(1):
                    contra_atacou = True
            else:
                acertos += 1
                dano_total += recebido
        verbo = "acerta" if acertos == 1 else "acertam"
        partes = [f"{acertos} {verbo} ({dano_total} de dano)"] if acertos else []
        if desvios:
            partes.append(f"você desvia de {desvios}")
        print(f"  {self.nome} atacam! {', '.join(partes)}. Vida: {heroi.vida}/{heroi.vida_max}")
        for nota in heroi.notas:
            print(f"  {nota}")
        heroi.notas = []
        if contra_atacou:
            print(f"  {heroi.nome} aproveita uma abertura e derruba um {self.nome_singular}! "
                  f"Restam {self.vivos()}.")
        if heroi.espinhos and acertos and self.matar(1):
            print(f"  Um {self.nome_singular} se fere nos espinhos e cai! Restam {self.vivos()}.")


class Aranha(Inimigo):
    """Mordida venenosa. A cada tanto, avisa e lança uma teia que prende o herói
    por um turno; depois disso fica exposta (recebe mais dano) e demora a tecer de novo."""

    def __init__(self, nome, duracao_veneno=3, dano_veneno=2, recarga_teia=3, turnos_exposta=2,
                 mult_exposta=1.25, **resto):
        super().__init__(nome, **resto)
        self.mult_exposto = mult_exposta
        self.duracao_veneno = duracao_veneno
        self.veneno_da_mordida = dano_veneno
        self.recarga_teia = recarga_teia
        self.turnos_exposta = turnos_exposta
        self.espera_teia = 1                 # turnos até poder avisar a teia
        self.tecendo = False

    def agir(self, heroi, turno):
        self.postura = None
        if self.tecendo:
            self.tecendo = False
            reacao = resolver_golpe(heroi, 2, f"{self.nome} lança uma TEIA!", atacante=self)
            if reacao != "esquivou":
                heroi.efeitos["preso"] = 1
                print("  Você está preso na teia e vai perder o próximo turno!")
            self.efeitos["vulneravel"] = self.turnos_exposta
            print(f"  Sem seda, {self.nome} fica exposta por {self.turnos_exposta} turnos!")
            self.espera_teia = self.recarga_teia
            return

        reacao = self.atacar(heroi, f"{self.nome} morde.")
        if reacao != "esquivou":
            if "veneno" not in heroi.efeitos:
                print("  Você foi envenenado!")
            heroi.efeitos["veneno"] = self.duracao_veneno     # renova, não acumula
            heroi.dano_continuo["veneno"] = self.veneno_da_mordida

        self.espera_teia -= 1
        if self.espera_teia <= 0:
            self.tecendo = True
            dica = DICA_ESQUIVAR if bom_de_esquiva(heroi) else "Ela vai mirar em você."
            print(f"  {self.nome} recua e começa a tecer uma teia... {dica}")


class Troll(Inimigo):
    """Alterna: ataca em um turno, se regenera no seguinte.
    A cada dois ataques, um é uma PANCADA (avisada antes) que deixa o herói tonto:
    ele perde o próximo turno, a menos que bloqueie ou esquive.
    Dano de fogo impede a próxima regeneração."""

    def __init__(self, nome, regeneracao=10, mult_pancada=1.2, **resto):
        super().__init__(nome, **resto)
        self.regeneracao = regeneracao
        self.mult_pancada = mult_pancada
        self.queimado = False               # vale até a próxima tentativa de regenerar

    def receber_ataque(self, dano, so_esquiva_ativa=False, inesquivavel=False,
                       alcance=1, elemento=None, fisico=False):
        recebido, reacao = super().receber_ataque(dano, so_esquiva_ativa, inesquivavel, alcance, elemento, fisico)
        if elemento == "fogo" and reacao != "esquivou":
            self.queimado = True
            self.notas.append(f"O fogo queima a pele de {self.nome}! Ele não vai conseguir se regenerar.")
        return recebido, reacao

    def agir(self, heroi, turno):
        # Ciclo de 4 turnos: 1 ataque, 2 regenera (+ aviso), 3 PANCADA, 4 regenera
        self.postura = None
        if turno % 4 == 3:
            self.pancada(heroi)
        elif turno % 2 == 1:
            self.atacar(heroi, f"{self.nome} esmaga com o porrete.")
        else:
            self.regenerar()
            if turno % 4 == 2:
                dica = DICA_ESQUIVAR if bom_de_esquiva(heroi) else DICA_BLOQUEAR
                print(f"  {self.nome} ergue o porrete bem alto... {dica}")
                return
        if turno % 2 == 1:
            print(f"  {self.nome} respira pesado... a carne dele começa a se fechar.")

    def pancada(self, heroi):
        dano = self.calcular_dano(heroi, multiplicador=self.mult_pancada)
        reacao = resolver_golpe(heroi, dano, f"{self.nome} desce o porrete com tudo!", atacante=self)
        if reacao is None and heroi.esta_vivo():
            heroi.efeitos["atordoado"] = 1
            print("  O mundo gira. Você está tonto e vai perder o próximo turno!")
        elif reacao == "bloqueou":
            print("  Sua guarda absorve o impacto: você continua firme.")

    def regenerar(self):
        if self.queimado:
            self.queimado = False
            print(f"  As queimaduras impedem {self.nome} de se regenerar!")
        else:
            curou = self.curar(self.regeneracao)
            print(f"  {self.nome} se regenera: +{curou} de vida.")


class KoboldsArmadilheiros(Enxame):
    """Enxame que, a cada tanto, avisa e dispara uma armadilha: prende o herói
    por um turno, a menos que ele esquive de propósito."""

    def __init__(self, nome, a_cada=3, dano_armadilha=5, **resto):
        super().__init__(nome, **resto)
        self.a_cada = a_cada
        self.dano_armadilha = dano_armadilha
        self.armando = False

    def agir(self, heroi, turno):
        if self.armando:
            self.armando = False
            reacao = resolver_golpe(heroi, self.dano_armadilha, "Uma armadilha dispara sob seus pés!",
                                    so_esquiva_ativa=True)
            if reacao != "esquivou":
                heroi.efeitos["preso"] = 1
                print("  Uma rede de correntes te prende! Você vai perder o próximo turno.")
            return
        super().agir(heroi, turno)
        if turno % self.a_cada == self.a_cada - 1 and self.vivos() > 0:
            self.armando = True
            print(f"  Um dos kobolds se abaixa e mexe em algo no chão, rindo... "
                  f"{dica_desviar_ou(heroi, 'Fique atento ao chão.')}")


class Golem(Inimigo):
    """Lento e muito blindado. Carrega um golpe num turno (avisado) e esmaga no seguinte.
    Golpes fortes RACHAM a armadura dele (perde defesa)."""

    def __init__(self, nome, limiar_rachar=8, perda_defesa=2, mult_esmagar=1.6, **resto):
        super().__init__(nome, **resto)
        self.limiar_rachar = limiar_rachar
        self.perda_defesa = perda_defesa
        self.mult_esmagar = mult_esmagar

    def receber_ataque(self, dano, so_esquiva_ativa=False, inesquivavel=False,
                       alcance=1, elemento=None, fisico=False):
        recebido, reacao = super().receber_ataque(dano, so_esquiva_ativa, inesquivavel, alcance, elemento, fisico)
        if recebido >= self.limiar_rachar and self.defesa > 0:
            self.defesa = max(0, self.defesa - self.perda_defesa)
            self.notas.append(f"A armadura de {self.nome} racha! Defesa: {self.defesa}.")
        return recebido, reacao

    def agir(self, heroi, turno):
        self.postura = None
        if turno % 2 == 1:
            print(f"  {self.nome} range as engrenagens e ergue os dois punhos... {DICA_BLOQUEAR}")
        else:
            self.atacar(heroi, f"{self.nome} ESMAGA o chão!", multiplicador=self.mult_esmagar)


class Berserker(Inimigo):
    """Quanto menos vida, mais forte: o ataque cresce conforme ele se machuca.
    Abaixo da metade da vida entra em FÚRIA: passa a atacar DUAS vezes por turno
    (cada golpe um pouco mais fraco), mas larga a guarda (defesa 0).
    Bloquear segura os dois; esquivar é um por um."""

    def __init__(self, nome, furia_max=0.6, mult_frenesi=0.75, **resto):
        super().__init__(nome, **resto)
        self.ataque_base = self.ataque
        self.furia_max = furia_max
        self.mult_frenesi = mult_frenesi
        self.enfurecido = False

    def agir(self, heroi, turno):
        perdido = 1 - self.vida / self.vida_max
        self.ataque = round(self.ataque_base * (1 + self.furia_max * perdido))
        self.postura = None
        if not self.enfurecido:
            super().agir(heroi, turno)
            if self.vida <= self.vida_max / 2:
                self.enfurecido = True
                self.defesa = 0
                print(f"  {self.nome} urra e entra em FÚRIA! Agora ele golpeia duas vezes "
                      f"por turno, mas sem se proteger. {DICA_BLOQUEAR}")
            return
        self.atacar(heroi, f"{self.nome} avança num frenesi de machadadas!", multiplicador=self.mult_frenesi)
        if heroi.esta_vivo():
            self.atacar(heroi, "...e golpeia de novo!", multiplicador=self.mult_frenesi)


class Capataz(Inimigo):
    """Escudo de torre: fica sempre na guarda (bloqueia muito), menos logo depois
    do golpe de martelo (avisado), quando fica ABERTO e exposto por um turno."""

    def __init__(self, nome, a_cada=3, mult_martelo=1.8, bloqueio_magia=0.5, **resto):
        super().__init__(nome, **resto)
        self.a_cada = a_cada
        self.mult_martelo = mult_martelo
        self.bloqueio_fisico = self.reducao_bloqueio
        self.bloqueio_magia = bloqueio_magia  # o escudo segura menos magia do que machado
        self.postura = "bloquear"           # já começa atrás do escudo

    def receber_ataque(self, dano, so_esquiva_ativa=False, inesquivavel=False,
                       alcance=1, elemento=None, fisico=False):
        self.reducao_bloqueio = self.bloqueio_fisico if fisico else self.bloqueio_magia
        return super().receber_ataque(dano, so_esquiva_ativa, inesquivavel, alcance, elemento, fisico)

    def decidir_se_defende(self):
        return False                        # a defesa dele é o escudo, não o comportamento padrão

    def agir(self, heroi, turno):
        if turno % self.a_cada == 0:
            self.postura = None
            self.atacar(heroi, f"{self.nome} gira o martelo por cima do escudo!",
                        multiplicador=self.mult_martelo)
            self.efeitos["vulneravel"] = 2  # diminui no começo do turno dele: vale 1 turno seu
            print(f"  O golpe desequilibra {self.nome}: o escudo baixa e ele fica ABERTO!")
            return
        self.postura = None
        self.atacar(heroi, f"{self.nome} golpeia com a ponta do escudo.")
        self.postura = "bloquear"
        if turno % self.a_cada == self.a_cada - 1:
            print(f"  {self.nome} recua atrás do escudo e ergue o martelo... "
                  f"{dica_desviar_ou(heroi, DICA_BLOQUEAR)}")


class Dragao(Inimigo):
    """Chefe em duas fases.
    1) Acima de metade da vida: garras + SOPRO de fogo (avisado), que não dá pra esquivar,
       só bloquear; deixa queimadura.
    2) Abaixo da metade: VOA. Golpes físicos têm chance de errar; magia e bombas acertam.
       O sopro vira um MERGULHO (avisado), que dá pra esquivar."""

    def __init__(self, nome, a_cada=3, mult_sopro=2.0, mult_mergulho=2.0, erro_em_voo=0.5,
                 queimadura=None, **resto):
        super().__init__(nome, **resto)
        self.a_cada = a_cada
        self.mult_sopro = mult_sopro
        self.mult_mergulho = mult_mergulho
        self.erro_em_voo = erro_em_voo
        self.queimadura = queimadura or {"turnos": 3, "dano": 4}
        self.voando = False
        self.anunciado = None               # o especial avisado é o que acontece, mesmo se mudar de fase

    def receber_ataque(self, dano, so_esquiva_ativa=False, inesquivavel=False,
                       alcance=1, elemento=None, fisico=False):
        if self.voando and fisico and not inesquivavel and random.random() < self.erro_em_voo:
            self.notas.append(f"{self.nome} está no ar, fora do seu alcance.")
            return 0, "esquivou"
        recebido, reacao = super().receber_ataque(dano, so_esquiva_ativa, inesquivavel, alcance,
                                                  elemento, fisico)
        if not self.voando and self.esta_vivo() and self.vida <= self.vida_max / 2:
            self.voando = True
            self.notas.append(f"{self.nome} ruge e LEVANTA VOO! Golpes com a arma vão ter "
                              f"dificuldade de alcançá-la; magia e bombas, não.")
        return recebido, reacao

    def agir(self, heroi, turno):
        self.postura = None
        if turno % self.a_cada == 0:
            especial = self.anunciado or ("mergulho" if self.voando else "sopro")
            self.anunciado = None
            if especial == "mergulho":
                dano = self.calcular_dano(heroi, multiplicador=self.mult_mergulho)
                resolver_golpe(heroi, dano, f"{self.nome} MERGULHA do alto!", atacante=self)
            else:
                dano = self.calcular_dano(heroi, multiplicador=self.mult_sopro, ignora_defesa=True)
                reacao = resolver_golpe(heroi, dano, f"{self.nome} solta um SOPRO DE FOGO!",
                                        inesquivavel=True, elemento="fogo", atacante=self)
                if heroi.esta_vivo():
                    heroi.efeitos["queimadura"] = self.queimadura["turnos"]
                    heroi.dano_continuo["queimadura"] = self.queimadura["dano"]
                    print("  As chamas grudam em você!")
            return

        self.atacar(heroi, f"{self.nome} {'ataca com as garras em rasante' if self.voando else 'golpeia com as garras'}.")
        if turno % self.a_cada == self.a_cada - 1:
            self.anunciado = "mergulho" if self.voando else "sopro"
            if self.voando:
                print(f"  {self.nome} sobe alto, entre as vigas da caverna... "
                      f"{dica_desviar_ou(heroi, DICA_BLOQUEAR)}")
            else:
                print(f"  {self.nome} enche o peito, e as escamas brilham em brasa... "
                      f"Isso vai cobrir tudo: {DICA_BLOQUEAR.lower()}")


class Desmorto(Inimigo):
    """Um herói de uma partida anterior, que morreu depois de ser revivido pelo Filactério
    e voltou como morto-vivo. Usa o especial da classe dele, sempre com aviso um turno antes."""

    ESPECIAIS = {
        "Guerreiro": "surto",
        "Mago": "bola_de_fogo",
        "Ladino": "furtivo",
    }

    def __init__(self, nome, classe, poder=0, a_cada=3, **resto):
        super().__init__(nome, **resto)
        self.classe = classe
        self.poder = poder
        self.a_cada = a_cada
        self.especial = None                 # (o "especial" genérico do Inimigo não é usado aqui)

    def avisar(self, heroi):
        tipo = self.ESPECIAIS.get(self.classe)
        if tipo == "surto":
            print(f"  {self.nome} ergue a arma e respira fundo, como você costumava fazer... {DICA_BLOQUEAR}")
        elif tipo == "bola_de_fogo":
            print(f"  Chamas se juntam nas mãos apodrecidas de {self.nome}... "
                  f"{dica_desviar_ou(heroi, DICA_BLOQUEAR)}")
        elif tipo == "furtivo":
            print(f"  {self.nome} some nas sombras... {dica_desviar_ou(heroi, DICA_BLOQUEAR)}")

    def usar_especial(self, heroi):
        tipo = self.ESPECIAIS.get(self.classe)
        if tipo == "surto":
            print(f"  {self.nome} usa um SURTO DE AÇÃO!")
            self.atacar(heroi, f"{self.nome} golpeia.")
            if heroi.esta_vivo():
                self.atacar(heroi, f"{self.nome} golpeia de novo.")
        elif tipo == "bola_de_fogo":
            dano = max(1, self.poder + random.randint(-2, 2))
            resolver_golpe(heroi, dano, f"{self.nome} lança uma BOLA DE FOGO!",
                           elemento="fogo", atacante=self)
        elif tipo == "furtivo":
            dano = self.calcular_dano(heroi, multiplicador=2.5, ignora_defesa=True)
            resolver_golpe(heroi, dano, f"{self.nome} surge pelas costas: ATAQUE FURTIVO!",
                           so_esquiva_ativa=True, atacante=self)
        else:
            self.atacar(heroi)

    def agir(self, heroi, turno):
        self.postura = None
        if turno % self.a_cada == 0:
            self.usar_especial(heroi)
            return
        self.atacar(heroi)
        if turno % self.a_cada == self.a_cada - 1:
            self.avisar(heroi)


TIPOS = {"enxame": Enxame, "aranha": Aranha, "troll": Troll,
         "kobolds": KoboldsArmadilheiros, "golem": Golem, "berserker": Berserker,
         "capataz": Capataz, "dragao": Dragao}


# Ajuste geral de dificuldade: multiplica a vida e o dano de TODOS os inimigos
# do inimigos.json. 1.0 = os valores do arquivo.
FORCA_GERAL = {"vida": 1.2, "ataque": 1.15}
# ...e um ajuste por andar ("forca_inimigos" no andares.json), trocado pelo
# jogo.jogar_campanha a cada andar novo.
forca_do_andar = {"vida": 1.0, "ataque": 1.0}
ATRIBUTOS_DA_FORCA = {"vida": ["vida", "vida_cada"], "ataque": ["ataque", "dano_cada", "dano_armadilha"]}


def criar_inimigo(chave):
    # O ** "abre" o dict do JSON como argumentos nomeados.
    # pop("tipo") tira o tipo dos dados e escolhe a classe (Inimigo se não tiver).
    dados_inimigo = dict(dados.INIMIGOS[chave])
    for grupo, fator in FORCA_GERAL.items():
        fator *= forca_do_andar.get(grupo, 1.0)
        for atributo in ATRIBUTOS_DA_FORCA[grupo]:
            if atributo in dados_inimigo and fator != 1:
                dados_inimigo[atributo] = max(1, round(dados_inimigo[atributo] * fator))
    classe = TIPOS.get(dados_inimigo.pop("tipo", None), Inimigo)
    return classe(**dados_inimigo)
