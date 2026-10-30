from random import randint
n = randint(1, 100)

print("Sorteei um número de 1 a 100")
c=1
while True:
    try:
        tentativa = int(input(f"Tentativa {c}: "))
        if tentativa < 0 or tentativa > 100:
            print("O número deve ser entre 0 e 100")
        elif tentativa > n:
            print(f"O número é menor que {tentativa}")
        elif tentativa < n:
            print(f"O número é maior que {tentativa}")
        else:
            print(f"Acertou! o numero era {n}")
            break
        c+=1
    except ValueError:
        print("deve inserir um número")