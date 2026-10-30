# Exercício 32 - Geradores
#
# Escreva um gerador com yield que produza a sequência de Fibonacci
# infinitamente: 0, 1, 1, 2, 3, 5, 8, 13...
# Pegue os 10 primeiros (pode usar next() ou itertools.islice).
# Pense: por que um loop infinito aqui não trava o programa?

def fibonacci():
    a, b = 0, 1
    while True:  
        yield b
        a, b = b, b + a



gen = fibonacci()
for _ in range(10):
    print(next(gen))