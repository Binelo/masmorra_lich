frase = input("Escreva uma frase: ")

nova_frase = []
for palavra in frase.split():
    nova_frase.append(palavra[0].upper() + palavra[1:])

print(" ".join(nova_frase))