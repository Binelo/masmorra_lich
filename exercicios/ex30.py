# Exercício 30 - dataclass
#
# Refaça uma classe simples (ex: Produto com nome, preco, quantidade)
# usando @dataclass (from dataclasses import dataclass).
# Compare com a versão normal: o que ela gera de graça?
# (teste print(produto) e produto1 == produto2)

from dataclasses import dataclass


class Produto:
    nome: str
    preco: float
    quantidade: int
    # def __init__(self, nome, preco, quantidade):
    #     self.nome = nome
    #     self.preco = preco
    #     self.quantidade = quantidade

@dataclass
class Produto2:
    nome: str
    preco: float
    quantidade: int
    # def __init__(self, nome, preco, quantidade):
    #     self.nome = nome
    #     self.preco = preco
    #     self.quantidade = quantidade

p1 = Produto()
p1.nome = "testes"
p1.preco = 55
p1.quantidade = 3
p2 = Produto2("teste2", 69, 77)

print(p1, p2)