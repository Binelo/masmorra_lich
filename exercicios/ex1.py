nome = input("Digite seu nome: ")
while True:
    try:
        idade = int(input("Digite sua idade: "))
        if idade >= 0 and idade <= 999:
            break
        else:
            print("Insira um número válido.")
    except ValueError:
        print("Apenas números inteiros são aceitos")


print(f"Olá {nome}, daqui a 10 anos voce terá {idade + 10} anos")