# Exercício 29 - Herança
#
# Crie a classe Animal com nome e um método falar().
# Crie as subclasses Cachorro e Gato, sobrescrevendo falar().
# Depois coloque vários animais numa lista e chame falar() de cada um no for
# (isso é polimorfismo). Pesquise também o que faz super().

class Animal:
    def __init__(self, nome):
        self.nome = nome

    def falar(self):
        return f"{self.nome} som!"

class Cachorro(Animal):
    def __init__(self, nome):
        super().__init__(nome)

    def falar(self):
        return f"{self.nome} au!"

class Gato(Animal):
    def __init__(self, nome):
        super().__init__(nome)

    def falar(self):
        return f"{self.nome} miau!"

a1 = Animal("texugo")
c1 = Cachorro("enrico")
g1 = Gato("tom")
lista = [a1, c1, g1]

for bicho in lista:
    print(bicho.falar())
