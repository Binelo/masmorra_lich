# Exercício 16 - Funções
#
# Crie a função calcular_imc(peso, altura) que RETORNA uma tupla
# (valor_do_imc, classificacao). Na hora de chamar, desempacote:
#   imc, classe = calcular_imc(80, 1.80)
#
# Classificação:
#   < 18.5 abaixo do peso | < 25 normal | < 30 sobrepeso | >= 30 obesidade

def calcular_imc(peso, altura):
    valor = peso / (altura**2)
    if valor < 18.5:
        return valor, "abaixo do peso"
    elif valor < 25:
        return valor, "normal"
    elif valor < 30:
        return valor, "sobrepeso"
    else:
        return valor, "obesidade"


imc, classe = calcular_imc(80, 1.80)

print(imc, classe)