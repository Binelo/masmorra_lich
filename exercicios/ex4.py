while True:
    try:
        n = int(input("Digite um número: "))
        break
    except ValueError:
        print("Apenas números inteiros são aceitos.")

if n > 0:
    print(f"{n} é positivo")
elif n < 0:
    print(f"{n} é negativo")
else:
    print(f"{n} é zero")