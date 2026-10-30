# A Masmorra do Lich

RPG de texto no terminal. Para jogar: `py main.py` dentro desta pasta.

## Onde fica cada coisa

| Arquivo | O que tem |
|---|---|
| `main.py` | Menu inicial (continuar / novo jogo / Santuário) e o fim de cada partida |
| `jogo.py` | Exploração: andar entre salas e os comandos (`pegar`, `status`...) |
| `batalha.py` | Combate por turnos (turno do herói, veneno, recompensas) |
| `golpes.py` | Como um golpe é resolvido (esquiva, bloqueio, contra-ataque) e as dicas |
| `inimigos.py` | `Inimigo`, os tipos especiais e `FORCA_GERAL` (dificuldade geral) |
| `personagens.py` | `Personagem` (base de todos), `Heroi`, `Guerreiro`, `Mago`, `Ladino` |
| `itens.py` | Pegar, usar, comprar e listar itens |
| `mapa.py` | Criar o mapa, descrever salas, andar, portas trancadas |
| `save.py` | Pausar a partida (`save.json`), que é apagado ao continuar |
| `progresso.py` | Ecos e Santuário: o que fica entre partidas (`progresso.json`) |
| `caido.py` | O herói caído (o Desmorto) e o arquivo `caido.json` |
| `dados.py` | Lê os arquivos JSON |
| `simular.py` | Simula centenas de partidas para testar o balanceamento |
| `dados/*.json` | Inimigos, itens, saque e a lista de andares |
| `dados/mapas/` | Um mapa por andar (`cripta.json`, `minas.json`) |

**Regra geral:** números e textos ficam no JSON; comportamento fica no Python.

## Andares
O jogo é uma sequência de andares, listados **em ordem** em `dados/andares.json`:
```json
{"id": "minas", "nome": "As Minas de Ferro-Negro", "mapa": "minas.json",
 "intro": "texto ao entrar", "conclusao": "texto ao vencer o chefe"}
```
Vencer o chefe de um andar: texto de conclusão, descanso (vida e energia cheias)
e começo do próximo andar com o mesmo herói. Vencer o chefe do
último andar é a vitória final. Para um andar novo: crie o mapa em `dados/mapas/`,
adicione a entrada no `andares.json` e uma rota em `ROTAS` no `simular.py`.

## Como adicionar...

### Um inimigo
Em `dados/inimigos.json`, crie uma chave nova:
```json
"aranha_pequena": {
  "nome": "Aranha Pequena", "vida": 20, "ataque": 7, "defesa": 1, "xp": 12, "ouro": 5,
  "esquiva": 0.15
}
```
Campos opcionais:
- `esquiva`, `reducao_bloqueio` (inimigos que bloqueiam se defendem quando estão fracos)
- `imune_veneno: true` (mortos-vivos e enxames)
- `fraquezas: {"fogo": 1.25, "gelo": 0.5}`: multiplica o dano daquele elemento
  (0 = imune; golpes **físicos** nunca caem abaixo de 0,5, a lâmina ainda corta)
- `elemento_ataque: "fogo"` e `efeito_ao_acertar: {"efeito": "queimadura", "turnos": 3, "dano": 2}`
- `embosca: true` (ataca antes de você agir, como o mímico)
- `drop: "glandula"` (item que ele sempre deixa ao morrer)
- `chefe`, `especial`, `texto_derrota` (veja abaixo)

Depois coloque `"inimigo": "aranha_pequena"` em alguma sala.

**Tipos com comportamento próprio** (campo `"tipo"`):
| tipo | comportamento | campos extras |
|---|---|---|
| `enxame` | vários bichos; golpe normal mata 1, área mata vários | `quantidade`, `vida_cada`, `nome_singular` |
| `aranha` | mordida envenena; avisa e lança teia (prende 1 turno), depois fica exposta | `duracao_veneno`, `recarga_teia`, `turnos_exposta` |
| `troll` | alterna atacar e regenerar; pancada avisada que atordoa; fogo impede a regeneração | `regeneracao`, `mult_pancada` |
| `kobolds` | enxame que arma armadilhas avisadas (prendem, só esquiva ativa evita) | `a_cada`, `dano_armadilha` + campos de enxame |
| `golem` | blindado; carrega (avisa) e esmaga; golpes fortes racham a armadura | `limiar_rachar`, `perda_defesa`, `mult_esmagar` |
| `berserker` | ataque cresce conforme perde vida | `furia_max` |
| `capataz` | sempre atrás do escudo, menos depois do golpe de martelo (fica exposto) | `a_cada`, `mult_martelo`, `bloqueio_magia` |
| `dragao` | chefe em 2 fases: sopro (só bloquear) e, abaixo de 50%, voo (físico erra; mergulho esquivável) | `mult_sopro`, `mult_mergulho`, `erro_em_voo`, `queimadura` |

Para um comportamento novo, crie uma subclasse de `Inimigo` em `inimigos.py`, sobrescreva
`agir(heroi, turno)` e registre no dicionário `TIPOS`.

### Um chefe com ataque especial
```json
"especial": {
  "texto": "solta uma TEIA VENENOSA!",
  "a_cada": 3,
  "multiplicador": 1.8,
  "ignora_defesa": true,
  "so_esquiva_ativa": true,
  "aviso": "prepara as fiandeiras..."
}
```
- `a_cada`: de quantos em quantos turnos o especial acontece (o aviso vem um turno antes)
- `multiplicador`: força em relação ao ataque normal
- `so_esquiva_ativa`: a esquiva passiva não pega, só quem escolher "Esquivar"
- `inesquivavel`: (opcional) nem a esquiva ativa pega, só o bloqueio

> JSON não aceita comentários (`//`). Se quiser anotar algo, anote fora do arquivo.
Derrotar qualquer inimigo com `"chefe": true` vence o jogo.

### Um item
Em `dados/itens.json`. Dois tipos:

**Equipamento** (tem `espaco`: `arma`, `escudo`, `armadura` ou `acessorio` — o herói usa até 2 acessórios):
```json
"botas": {
  "nome": "Botas Leves", "descricao": "Esquiva +5%.",
  "espaco": "acessorio", "bonus": {"esquiva": 0.05}
}
```
- `bonus` pode ter vários atributos e valores negativos: `{"ataque": 4, "esquiva": -0.05}`
- atributos possíveis: `ataque`, `defesa`, `esquiva`, `reducao_bloqueio`, `vida_max`, `energia_max`,
  `poder` (só Mago), e os de efeito especial:
  - `roubo_vida: 0.3` cura 30% do dano dos seus golpes físicos
  - `chance_atordoar: 0.2` 20% de o inimigo perder o turno (chefes resistem)
  - `espinhos: 3` quem te acerta toma 3 de dano
  - `cura_defensiva: 3` esquivar/bloquear com sucesso cura 3 (uma vez por turno)
- `"elemento": "fogo"` (arma): seus golpes físicos são de fogo
- `"reviver": 0.4`: ao morrer, volta com 40% da vida e o item quebra
- `resistencia_fogo: 0.4` (bonus): -40% de dano de fogo recebido
- `"troca_habilidade": {"nome_habilidade": "Lança de Gelo", "elemento_habilidade": "gelo"}`:
  muda a habilidade enquanto equipado (Tomo do Inverno)
- `"classes": ["Mago"]` restringe quem pode equipar
- `"valor": 20` é o preço de referência: vender paga a metade. `"vendivel": false` impede a venda (só a chave usa isso)
- pegar com o espaço vazio equipa na hora; com o espaço ocupado vai pra mochila (comando `equipar`)

**Consumível** (`"tipo": "consumivel"`), some ao usar:
```json
"elixir": {"nome": "Elixir", "descricao": "Recupera 50 de vida.", "tipo": "consumivel", "cura": 50}
```
Efeitos: `cura` (vida), `energia`, `cura_efeito: "queimadura"`, `envenena_arma`, `congelar` (inimigo perde o turno),
`dano` (no inimigo, só em combate; com `alcance: 99` atinge enxames inteiros e `elemento: "fogo"`).

### Onde os itens aparecem
- **Fixo numa sala:** `"itens": ["chave"]` no `mapa.json`. Use para itens importantes.
- **Sorteado:** `"saque": [{"tabela": "armas", "chance": 0.5}]` na sala. O sorteio acontece ao
  criar o jogo e ignora itens que a classe do herói não pode usar.
- **Tabelas de saque** ficam em `dados/saque.json`, com pesos (peso 6 sai 3x mais que peso 2):
  ```json
  "armas": {"espada": 5, "adaga": 4, "machado": 2, "cajado": 2}
  ```
- **Numa sala sorteada:** `"itens_espalhados"` no topo do `mapa.json` (é assim que a chave funciona):
  `{"item": "chave", "salas": ["arsenal", "cripta", "ponte"]}`
- **Deixado por um inimigo:** `"drop": "coracao"` (sempre esse) ou `"drop_tabela": "reliquias_lich"`
  (um item sorteado da tabela, como as relíquias do Lich).
- **Num baú:** `"bau": {"tabela": "armas_minas", "chance_mimico": 0.4}` na sala (comando `abrir`).
  O baú pode ser um mímico; vencendo, o tesouro cai no chão.
- **À venda:** na sala do mercador, `"mercador": {"pocao": 10, "botas": 40}`.
  Até o chefe dá pra juntar uns 29 de ouro, então itens a 30+ só aparecem achando.

### Um NPC
Na sala: `"npc": {"nome": "Kyrzathul, o Infindável", "falas": ["...", "..."]}`.
O comando `falar` sorteia uma fala. Junto com `"mercador"`, vira um vendedor com personalidade.

### Uma sala
Em `dados/mapa.json`, dentro de `"salas"`, crie a sala e **ligue as saídas nos dois sentidos**
(se a sala A tem `"leste": "b"`, a sala B precisa de `"oeste": "a"`).
Atualize o `"desenho"` do mapa e, se a rota mudar, a `ROTA` no `simular.py`.

### Uma classe de herói
Tipos de habilidade disponíveis (atributos de classe):
- golpe (padrão): `usar_habilidade(alvo)` devolve `(dano, texto)`
- `alcance_habilidade`: quantos alvos de um enxame atinge (Mago: todos)
- `elemento_habilidade = "fogo"`: magia que não usa a arma (Mago)
- `atordoar_habilidade = 0.5`: chance de atordoar (chefes resistem)
- `acoes_extras_habilidade = 2`: não ataca, dá ações extras no turno (Surto de Ação do Guerreiro).
  Em `batalha.py`, `SURTO_PERMITE_DEFESA` decide se as ações extras podem ser esquivar/bloquear.


Em `personagens.py`: subclasse de `Heroi` com `nome_habilidade`, `custo_habilidade`,
`esquiva`, `reducao_bloqueio`, `descricao`, um `__init__` com os atributos e um
`usar_habilidade(alvo)` que **devolve** `(dano, texto)`. Depois adicione em `CLASSES`.

## Roguelite: morte permanente, Ecos e Santuário
- **Morte permanente.** `salvar` é só pra pausar: grava e fecha o jogo. Ao continuar,
  o save é apagado (fechar o jogo no meio = perder a partida). Morrer, vencer ou
  abandonar (`sair` sem salvar) encerra a partida.
- **Ecos.** No fim de toda partida: 1 Eco a cada 5 de XP, +20 por andar concluído,
  +40 por vencer tudo (`progresso.py`).
- **Santuário** (menu inicial): melhorias permanentes compradas com Ecos, aplicadas
  a todo herói novo. Ficam em `dados/santuario.json`:
  ```json
  {"id": "vigor", "nome": "Vigor", "descricao": "...", "atributo": "vida_max", "por_nivel": 5,
   "custos": [20, 35, 55, 80, 110]}
  ```
  (também aceita `"item"`, `"ouro"` e `"tabela_inicial"` no lugar de `"atributo"`).
- **Fontes** só podem ser bebidas uma vez.
- **Dificuldade geral:** `FORCA_GERAL` no `inimigos.py` multiplica vida e dano de todos
  os inimigos do JSON (hoje 1.2 de vida e 1.15 de dano).

## Depois de mudar números
Rode `py simular.py` (herói novo, sem melhorias) e `py simular.py 300 max` (todas as
melhorias do Santuário). Metas atuais, seguindo as dicas dos inimigos:
- sem melhorias: ~30-50% vencem o Lich, ~5-15% vencem as Minas também;
- com tudo comprado: ~90-100%.
Como os itens são sorteados, rode com bastante partidas (`py simular.py 500` ou mais).

## Relíquias do Lich
O Lich deixa UMA relíquia sorteada da tabela `reliquias_lich` (Coroa, Foice Sombria, Manto, Filactério).
Por enquanto o jogo termina no Lich, mas a relíquia já fica no inventário e no save,
pronta para quando houver próximos andares.

## Efeitos em combate
- **Veneno / Queimadura:** dano depois de cada ação (sua e do inimigo). Renovam, não acumulam.
  Acabam no fim da luta, ou com Antídoto / Unguento.
- **Preso** (teia): perde o próximo turno.
- **Exposto:** recebe +50% de dano.
- **Atordoado / congelado:** perde o próximo turno (a pancada do Troll faz isso com o herói, a menos que ele bloqueie ou esquive).
  Chefes e mini-chefes (`resiste_controle`) resistem ao atordoar/congelar das armas e bombas;
  só itens de "congelar" funcionam neles.
- Efeitos do herói diminuem no fim do turno dele; os do inimigo, no início do turno dele.

## Padrão: mini-chefes deixam itens únicos
Todo mini-chefe tem um `"drop"` que só aparece com ele (não está em loja nem em saque):
| Andar | Mini-chefe | Drop |
|---|---|---|
| Cripta | Aranha Gigante | Glândula de Veneno |
| Cripta | Troll da Ponte | Coração de Troll |
| Minas | Golem de Ferro | Núcleo do Golem |
| Minas | Anão Berserker | Braçadeira da Fúria |
| Minas | Capataz Anão | Escudo de Torre |

Chefes deixam um item fixo + uma relíquia sorteada (`"drop"` + `"drop_tabela"`).

## Os heróis caídos (e como nascem os Liches)
O Filactério devolve a vida, mas cobra um preço: quem morre **depois** de ter sido revivido
por ele não descansa. Volta como morto-vivo e, se não for destruído, vira um Lich.
Tudo fica em `caido.json` (apagar o arquivo "esquece" todos). Os números estão no topo de `caido.py`.

- **Registro:** até 3 caídos (`MAXIMO`); um novo substitui o mais antigo que ainda não é Lich.
- **Título:** sorteado entre os que combinam com a partida dele: itens equipados
  (Adaga Vampírica -> "o Bebedor de Sangue"), chefes derrotados ("o Matador de Liches"),
  ouro ("o Avarento"), nível baixo ("o Imprudente")... Listas `TITULOS_POR_ITEM` e `TITULOS_POR_ABATE`.
- **Aparecer:** num mapa novo do andar onde morreu, cada caído rola a sua chance (começa em 60%).
  Quem não aparece continua na lista.
- **Luta:** 80% da vida e do ataque que tinha (sobe com os passos), imune a veneno, fraco a fogo,
  e o especial da classe com aviso um turno antes.
- **Fugir:** chance -20 pontos (mínimo 10%), +1 passo, +10% de força.
- **Derrotar:** metade do ouro e dos itens, mais XP. Chance de voltar: 15%, +10% a cada derrota
  (máximo 45%). Se voltar, ganha +1 passo; senão, descansa e sai da lista.
- **3 passos:** vira **Lich-caído** ("Fulano, o Lich"). Só um por vez: enquanto ele existir,
  os outros param em 2 passos.
- **Lich-caído:** mata um mini-chefe do andar e toma a sala dele (os restos ficam no chão).
  Usa os atributos do Lich original x `forca_lich_caido` do andar (no `andares.json`), o ataque do
  herói se for maior, e o Raio Sombrio. Derrotado: metade do ouro e dos itens, um Filactério e uma
  relíquia melhorada (tabela `reliquias_lich_plus`), e sai da lista.
- O `simular.py` desliga tudo isso (`caido.ATIVO = False`).
