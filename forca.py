import random

categorias = {
    "paises": [
        'brasil', 'australia', 'japao', 'canada', 'gana', 'grecia', 'peru',
        'china', 'chile', 'cuba', 'belgica', 'polonia', 'jamaica', 'paraguai',
        'alemanha', 'zimbabue', 'argentina', 'dinamarca', 'madagascar',
        'eslovaquia', 'montenegro', 'mexico', 'franca', 'italia', 'espanha',
        'portugal', 'inglaterra', 'escocia', 'irlanda', 'islandia', 'noruega',
        'suecia', 'finlandia', 'russia', 'ucrania', 'croacia', 'hungria',
        'austria', 'suica', 'holanda', 'turquia', 'egito', 'marrocos',
        'nigeria', 'angola', 'mocambique', 'quenia', 'etiopia', 'senegal',
        'camaroes', 'tunisia', 'india', 'paquistao', 'tailandia', 'vietna',
        'indonesia', 'filipinas', 'mongolia', 'nepal', 'coreia', 'iraque',
        'colombia', 'venezuela', 'equador', 'bolivia', 'uruguai', 'honduras',
        'guatemala', 'panama', 'nicaragua', 'haiti', 'groenlandia',
        'luxemburgo', 'cazaquistao', 'uzbequistao',
        'azerbaijao', 'bangladesh', 'botsuana', 'namibia',
        'samoa', 'tuvalu', 'fiji', 'vanuatu', 'butao', 'malta', 'chipre',
    ],
    "animais": [
        'cachorro', 'gato', 'elefante', 'girafa', 'tartaruga', 'jacare',
        'capivara', 'tamandua', 'ornitorrinco', 'pinguim', 'golfinho',
        'tubarao', 'polvo', 'camaleao', 'hipopotamo', 'rinoceronte',
        'canguru', 'coala', 'texugo', 'lontra', 'morcego', 'coruja',
        'papagaio', 'tucano', 'flamingo', 'avestruz', 'escorpiao', 'formiga',
        'borboleta', 'joaninha', 'caranguejo', 'cavalo', 'zebra', 'leopardo',
        'guepardo', 'lobo', 'raposa', 'esquilo', 'preguica', 'tatu',
    ],
    "comidas": [
        'lasanha', 'feijoada', 'coxinha', 'pastel', 'brigadeiro', 'pudim',
        'churrasco', 'pizza', 'hamburguer', 'sushi', 'macarrao', 'panqueca',
        'tapioca', 'acai', 'pipoca', 'sorvete', 'chocolate', 'mandioca',
        'moqueca', 'risoto', 'estrogonofe', 'empada', 'quindim', 'farofa',
        'polenta', 'cuscuz', 'omelete', 'torrada', 'biscoito', 'abacaxi',
        'melancia', 'morango', 'jabuticaba', 'maracuja', 'brocolis',
        'cenoura', 'abobora', 'beterraba',
    ],
    "objetos": [
        'cadeira', 'tesoura', 'travesseiro', 'espelho', 'relogio', 'mochila',
        'lanterna', 'grampeador', 'calculadora', 'ventilador', 'geladeira',
        'liquidificador', 'microondas', 'vassoura', 'escova', 'chave',
        'cadeado', 'garrafa', 'caneca', 'panela', 'colher', 'martelo',
        'parafuso', 'teclado', 'monitor', 'controle', 'fone', 'carregador',
        'tomada', 'caderno', 'borracha', 'apontador', 'envelope', 'binoculo',
        'bussola', 'termometro', 'guitarra', 'bateria', 'violino',
    ],
    "profissoes": [
        'medico', 'professor', 'bombeiro', 'engenheiro', 'programador',
        'astronauta', 'veterinario', 'arquiteto', 'jornalista', 'advogado',
        'eletricista', 'encanador', 'padeiro', 'cozinheiro', 'motorista',
        'piloto', 'carteiro', 'dentista', 'fotografo', 'psicologo',
        'marceneiro', 'jardineiro', 'cientista', 'bibliotecario',
        'farmaceutico',
    ],
    "esportes": [
        'futebol', 'basquete', 'volei', 'tenis', 'natacao', 'ciclismo',
        'atletismo', 'handebol', 'boxe', 'judo', 'karate', 'surfe', 'skate',
        'xadrez', 'golfe', 'rugbi', 'beisebol', 'esgrima', 'escalada', 'remo',
        'canoagem', 'paraquedismo', 'hipismo', 'badminton', 'triatlo',
    ],
}

desenhos = [
r"""
  +---+
  |   |
      |
      |
      |
      |
=========""",
r"""
  +---+
  |   |
  O   |
      |
      |
      |
=========""",
r"""
  +---+
  |   |
  O   |
  |   |
      |
      |
=========""",
r"""
  +---+
  |   |
  O   |
 /|   |
      |
      |
=========""",
r"""
  +---+
  |   |
  O   |
 /|\  |
      |
      |
=========""",
r"""
  +---+
  |   |
  O   |
 /|\  |
 /    |
      |
=========""",
r"""
  +---+
  |   |
  O   |
 /|\  |
 / \  |
      |
=========""",
]

cat = random.choice(list(categorias))

palavra_escolhida = random.choice(categorias[cat])
lista_tentativas = []
lista_tentativas_erradas = []

def montar_palavra():
    chute = []
    for l in palavra_escolhida:
        if l in lista_tentativas:
            chute.append(l)
        else:
            chute.append("_")
    return chute

def verificar_tentativa(tentativa):
    if len(tentativa) > 1 and tentativa == palavra_escolhida:
        print(f"Você ganhou! a palavra era {palavra_escolhida}")
        return True
    elif tentativa in palavra_escolhida:
        lista_tentativas.append(tentativa)
        chute = montar_palavra()
        if "".join(chute) == palavra_escolhida:
            print(f"Você ganhou! a palavra era {palavra_escolhida}")
            return True
    else:
        lista_tentativas_erradas.append(tentativa)
        print(f"errou, você tem mais {len(desenhos) - 1 - len(lista_tentativas_erradas)} chances")


def ler_tentativa():
    while True:
        tentativa = input(f'Erradas: {" ".join(lista_tentativas_erradas)}\nDigite uma letra: ').lower()

        if tentativa == palavra_escolhida:
            return tentativa
        if len(tentativa) != 1 or not tentativa.isalpha():
            print("Digite apenas uma letra.")
        elif tentativa in lista_tentativas or tentativa in lista_tentativas_erradas:
            print("Você já tentou essa letra.")
        else:
            return tentativa
        
print(f'A categoria é {cat}')
while True:
    if len(lista_tentativas_erradas) >= len(desenhos) - 1:
        print(desenhos[-1])
        print(f"As tentativas acabaram. A palavra era {palavra_escolhida}")
        break
    print(desenhos[len(lista_tentativas_erradas)])
    print(" ".join(montar_palavra()))
    tentativa = ler_tentativa()
    if verificar_tentativa(tentativa):
        break
