# Plano: Fase 2

**Status: implementado.** Mudanças em relação ao plano estão no fim do arquivo.

---

## 1. Como os andares vão funcionar (parte técnica)

**Ideia:** derrotar o chefe de um andar leva ao próximo, com o mesmo herói
(nível, equipamento, ouro, itens e relíquias).

- `dados/andares.json` com a lista de andares em ordem:
  ```json
  [
    {"id": "cripta", "nome": "A Cripta do Lich", "mapa": "cripta.json",
     "intro": "Dizem que um Lich governa este lugar..."},
    {"id": "minas", "nome": "As Minas de Ferro-Negro", "mapa": "minas.json",
     "intro": "Atrás do trono, uma escada desce para o calor..."}
  ]
  ```
- O `mapa.json` atual vira `dados/mapas/cripta.json`. O `inimigos.json`, o `itens.json`
  e o `saque.json` continuam únicos (cada mapa só usa os inimigos que quiser).
- Ao vencer o chefe de um andar (e não for o último):
  1. texto de encerramento do chefe
  2. **descanso**: vida e energia cheias (a fonte do andar seguinte já não é obrigatória)
  3. **save automático**
  4. texto de introdução do próximo andar e `criar_mapa(andar)`
- Vencer o chefe do **último** andar é a vitória final.
- O save passa a guardar `"andar"`. Saves antigos são tratados como `"cripta"`.
- Não dá para voltar a um andar anterior (simplifica o save e o equilíbrio).
- `simular.py`: uma rota por andar, e o relatório passa a mostrar a taxa de vitória
  e a de chegada ao chefe **por andar**.

**Força do herói ao chegar:** pelas simulações, ele termina a cripta perto do nível 5,
com Filactério + 1 relíquia, e com uns 60 de ouro. O andar 2 é calibrado para isso.

---

## 2. Tema proposto: As Minas de Ferro-Negro

O Lich guardava a passagem para antigas minas anãs. Elas foram tomadas por
**Ignarax, uma dragoa jovem**, e pelos kobolds que a servem. O tema é **fogo e metal**,
o contrário da cripta (mortos-vivos, fracos a fogo, imunes a veneno). Assim, o que era
fácil no andar 1 deixa de ser:

- o **fogo do Mago** perde força (elementais e a dragoa resistem a fogo);
- o **veneno da arma** volta a ser útil (kobolds e anões são vivos);
- aparece o **gelo** como resposta nova (itens, e uma opção para o Mago).

Outros temas que considerei: **Catacumbas Alagadas** (afogados, água, correnteza)
e **Floresta de Fungos** (esporos, venenos, plantas que se regeneram).
Dá pra trocar o tema sem mudar a parte técnica.

### Um NPC: o kobold que jura ser um dragão
Entre os kobolds, um não serve a Ignarax: **Kyrzathul, o Infindável**, que garante ser um
dragão ancião preso num corpo de kobold, e chama Ignarax de "filhote usurpadora".
Ele seria o **mercador do andar 2**, arrogante e engraçado, e ninguém sabe se ele fala a
verdade. Pede um comando novo, `falar`, com falas sorteadas de uma lista no JSON.

---

## 3. Inimigos

Cada um testa algo diferente e reaproveita os sistemas que já existem.

| Inimigo | Tipo | Mecânica | Quem sofre / quem brilha |
|---|---|---|---|
| **Kobolds Armadilheiros** | enxame (4) | a cada 3 turnos, armam uma armadilha (avisada) que **prende** | Mago e bombas resolvem; o Ladino desvia |
| **Golem de Ferro** | novo | **defesa 8**, imune a veneno; cada golpe forte (≥ 12) **racha a armadura** (-2 de defesa) | Surto do Guerreiro e críticos do Ladino; ataques fracos quase não passam |
| **Elemental de Brasa** | novo | **imune a fogo**, fraco a gelo; o toque causa **queimadura** (dano por turno, como o veneno) | o Mago precisa de outra estratégia |
| **Anão Berserker** | novo | quanto menos vida, **mais ataque** | matar rápido ou se defender no fim |
| **Mímico** | evento | um baú no chão às vezes é um monstro (sorteado ao criar o mapa) | surpresa; ensina a desconfiar de baús |

**Mini-chefe: o Capataz Anão.** Escudo de torre: **bloqueia** quase tudo de frente,
mas depois de cada ataque pesado (avisado) fica **aberto** por um turno.
Recompensa: **Escudo de Torre** (bloqueio +10%).

---

## 4. Chefe: Ignarax, a Dragoa de Brasa

Duas fases:

1. **Acima de 50% de vida:** a cada 3 turnos, **Sopro de Fogo** (avisado). Só dá pra se
   proteger **bloqueando**: ele cobre a sala inteira, então esquivar não funciona. Deixa
   queimadura.
2. **Abaixo de 50%:** ela **levanta voo**. Ataques físicos têm 50% de chance de errar, mas
   magias e bombas acertam normal. O sopro vira um **mergulho** que pode ser esquivado
   (a vez do Ladino brilhar).

Resistências: fogo × 0,5, gelo × 1,5. Drop: **Escama de Ignarax** (resistência a fogo) +
1 item de um "kit da dragoa" sorteado, igual ao Lich.

---

## 5. Sistemas novos que isso pede

- **Queimadura:** um segundo efeito de dano por turno. Dá pra generalizar o veneno em
  "efeitos de dano por turno" (cada um com o próprio dano e a própria cura).
- **Elemento gelo:** itens e fraquezas. O dicionário `fraquezas` já aceita valores
  menores que 1, então resistências como `{"fogo": 0.5}` já funcionam.
- **Inimigo com fases** (subclasse `Dragao`) e **armadura que racha** (subclasse `Golem`).
- **Eventos de sala:** baú/mímico (e talvez armadilhas no chão).
- **NPC com falas** (comando `falar`).
- **Andares** (seção 1).

---

## 6. Itens da fase 2 (onde o ouro guardado vale a pena)

Vendidos pelo Kyrzathul, entre 40 e 120 de ouro. Os inimigos do andar 2 dão mais ouro.

| Item | Tipo | Efeito |
|---|---|---|
| Lâmina Gélida | arma | golpes de gelo; 15% de chance de congelar |
| Tomo do Inverno | acessório (Mago) | a Bola de Fogo vira **Lança de Gelo** (troca o elemento da habilidade) |
| Armadura de Escamas | armadura | resistência a fogo (-40% de dano de fogo) |
| Anel do Predador | acessório (Ladino) | crítico base +15% |
| Manoplas do Titã | acessório (Guerreiro) | Surto de Ação dá 3 ações |
| Poção Grande | consumível | cura 60 |
| Unguento | consumível | cura queimadura |
| Bomba de Gelo | consumível | área, gelo, congela por 1 turno |

---

## 7. Mapa (rascunho, umas 9 salas)

```
                    [Covil de Ignarax]
                            |
   [Forja]-----------[Salão dos Reis]-----------[Fornalha]
      |                     |                       |
[Depósito]          [Barracas Kobold]         [Poço de Lava]
      |                     |                       |
   [Trilhos]---------[Entrada das Minas]------[Loja do Kyrzathul]
```
- Chave do covil: **sorteada**, como na cripta (talvez com o Capataz).
- Uma sala de descanso (forja abandonada com água de resfriamento?).

---

## 8. Metas de equilíbrio (as mesmas da cripta)

- Seguindo as dicas: **85–95%** de vitória no andar 2, para as três classes.
- Ignorando as dicas: bem menos.
- Chegar vivo ao chefe: **90% ou mais**.
- Mini-chefe: tirar **35–50%** da vida; inimigos comuns, menos que isso.

---

## 9. Ordem de implementação sugerida

1. **Sistema de andares** + mover a cripta para `dados/mapas/` (o jogo continua igual)
2. Queimadura (generalizar o veneno) e elemento gelo
3. Inimigos novos, um por vez, testando cada um
4. Capataz e Ignarax
5. Mapa das minas, saque e loja
6. Kyrzathul e o comando `falar`
7. Simular e calibrar o andar 2 inteiro

---

## Decisões tomadas
- Tema: **As Minas de Ferro-Negro**, como descrito acima.
- **Kyrzathul** entra como mercador do andar 2.
- O herói **recupera tudo** entre os andares (descanso + save automático).
- Inimigos da cripta podem voltar mais fortes, **só os que fazem sentido no local**
  (ex.: morcegos nas galerias, aranhas em túneis abandonados; mortos-vivos não).

## Diferenças em relação ao plano (o que mudou na implementação)
- Mímico: é um baú (comando `abrir`) no Depósito e nas Barracas, não uma sala.
- Aranha das Galerias e Morcegos de Fuligem voltam como versões mais fortes.
- Capataz: o escudo segura 70% de golpes físicos mas só 30% de magia.
- Ignarax: cumpre sempre o especial que anunciou, mesmo se mudar de fase no meio.
- Golpes físicos nunca causam menos de 50% num inimigo imune ao elemento da arma.
- Ladino: vida inicial 38 -> 42 (estava atrás nos dois andares).
