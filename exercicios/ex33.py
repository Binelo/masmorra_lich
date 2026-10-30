# Exercício 33 - Decorators
#
# Crie um decorator @cronometro que mede e imprime quanto tempo
# uma função leva para rodar (use time.perf_counter()).
# Teste em uma função lenta, ex: somar números de 1 a 10 milhões.
# Extra: use functools.wraps e descubra por que ele existe.

import time

def funcao():
    start = time.perf_counter()
    soma = 0
    for i in range(1, 10000000):
        soma+= i
    print(soma)
    end = time.perf_counter()
    print(f"Tempo decorrido: {end - start:.2f} segundos")

funcao()