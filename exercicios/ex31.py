# Exercício 31 - property
#
# Crie uma classe Pessoa onde idade é validada com @property:
# idade não pode ser negativa (lance ValueError).
#   p = Pessoa("Ana", 30)
#   p.idade = -5   -> deve dar erro

class Pessoa:
    def __init__(self, nome, idade):
        self.nome = nome
        self.idade = idade

    @property
    def idade(self):
        return self._idade

    @idade.setter
    def idade(self, value):
        if value < 1:
            raise ValueError("Idade não pode ser negativa")
        self._idade = value

p = Pessoa("Ana", 30)
p.idade = -5