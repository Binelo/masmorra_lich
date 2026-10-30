# Exercício 28 - Classes
#
# Crie a classe ContaBancaria com:
#   - titular e saldo (saldo começa em 0)
#   - depositar(valor)
#   - sacar(valor): lança uma exceção (raise ValueError) se não tiver saldo
#   - __str__ que mostre algo como "Conta de Ana - saldo: R$ 150.00"
# Teste o saque sem saldo dentro de um try/except.

class ContaBancaria:
    def __init__(self, titular, saldo):
        self.titular = titular
        self.saldo = saldo

    def depositar(self, valor):
        self.saldo = (self.saldo + valor) if valor > 1 else self.saldo + 0

    def sacar(self, valor):
        if valor > self.saldo:
            raise ValueError("Você nao tem saldo o suficiente")
        else:
            self.saldo = (self.saldo - valor) if valor > 1 else self.saldo - 0

    def __str__(self):
        return f"Conta de {self.titular} - saldo: R$ {self.saldo}"


c1 = ContaBancaria("João", 100)
print(c1)
c1.depositar(100)
print(c1)
c1.sacar(100)
print(c1)