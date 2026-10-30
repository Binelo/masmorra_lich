# Exercício 14 - Sets
#
# Dadas duas listas, mostre usando set:
#   - os elementos em comum
#   - os que só existem na primeira
#   - os que só existem na segunda
#
# Exemplo: a = [1, 2, 3, 4], b = [3, 4, 5, 6]
#   comum: {3, 4} | só a: {1, 2} | só b: {5, 6}

a = [1, 2, 3, 4]
b = [3, 4, 5, 6]

a = set(a)
b = set(b)

print(f"comum: {a & b}")
print(f"só a: {a - b}")
print(f"só b: {b - a}")
print(f"exclusivos b: {b ^ a}")