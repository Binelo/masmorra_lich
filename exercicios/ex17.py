# Exercício 17 - Funções
#
# Crie uma função com parâmetro padrão:
#   saudacao(nome, cumprimento="Olá")
#
# saudacao("Binelo")            -> "Olá, Binelo!"
# saudacao("Binelo", "E aí")    -> "E aí, Binelo!"
# Teste também chamando com argumento nomeado: saudacao(cumprimento="Oi", nome="Ana")

def saudacao(nome="Ana", cumprimento="Olá"):
    print(f"{cumprimento}, {nome}")

saudacao("Binelo")
saudacao("Binelo", "E aí")
saudacao()