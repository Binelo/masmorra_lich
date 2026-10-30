palavra = input("Escreva uma palavra ou frase: ")

limpa = palavra.lower().replace(" ", "")

if limpa == limpa[::-1]:
    print(f'"{palavra}" é palíndromo')
else:
    print(f'"{palavra}" não é palíndromo')