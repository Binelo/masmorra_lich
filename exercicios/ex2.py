while True:
    try:
        n1 = int(input("digite o primeiro número: "))
        n2 = int(input("digite o segundo número: "))
        if n2 == 0:
            n2 = int(input("O segundo número não pode ser 0: "))
        break
    except ValueError:
        print("apenas números inteiros são aceitos.")

print(f"soma: {n1 + n2}")
print("divisão: ", n1 / n2)
print("divisão inteira: ", n1 // n2)
print("resto: ", n1 % n2)
print("potência: ", n1 ** n2)
