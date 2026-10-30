# Exercício 18 - Funções
#
# 1) Crie somar(*args), que soma qualquer quantidade de números.
#    somar(1, 2) -> 3 | somar(1, 2, 3, 4) -> 10
# 2) Crie montar_perfil(**kwargs), que imprime cada chave e valor.
#    montar_perfil(nome="Ana", cidade="Joinville") ->
#      nome: Ana
#      cidade: Joinville
# Descubra de que tipo são args e kwargs dentro da função (use type()).

def somar(*args):
    soma = 0
    for n in args:
        soma += n
    return soma

def montar_perfil(**kwargs):
    for key, value in kwargs.items():
        print(f"{key}: {value}")


print(somar(6, 7, 7, 6, 7, 7))
montar_perfil(nome="Joao", cidade="Joinville")