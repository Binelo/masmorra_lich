# o código precisa imprimir os numeros de 1 a 100, mas caso o 
# número seja divisível por 3 deve printar Fizz, e caso o 
# número seja divisível por 5 deve printar Buzz, e caso o
# número seja divisivel por 3 e 5 deve printar FizzBuzz
# para isso tenho que fazer um while com contado que começa no 1 e vai
# até 100, posso usar o contador para fazer os prints e ifs
# todo loop eu faço um if para ver se o resto do contador com 3
# e o resto com 5 ambos dão 0, se não faço apenas com um dos dois para
# saber se vou printar fizz e buzz, senão printo o número

for c in range(1, 101):
    if c % 3 == 0 and c % 5 == 0:
        print("FizzBuzz")
    elif c % 3 == 0:
        print("Fizz")
    elif c % 5 == 0:
        print("Buzz")
    else:
        print(c)