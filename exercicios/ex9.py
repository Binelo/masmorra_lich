frase = input("Escreva uma frase: ")

vogais = "aeiouáéíóúâêôãõà"
encontradas = []

for letra in frase.lower():
    if letra in vogais:
        encontradas.append(letra)

print(f"A frase tem {len(encontradas)} vogais: {encontradas}")