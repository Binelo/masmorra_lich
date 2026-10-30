while True:
    try:
        c = float(input("Digite uma temperatura em Celsius: "))
        break
    except ValueError:
        print("Deve ser um número")

f = c*1.8 + 32
print(f"Temperatura em Fahrenheit: {f:.2f}")