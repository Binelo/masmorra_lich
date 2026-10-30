LINHAS = 20
COLUNAS = 20

grade = [[0] * COLUNAS for _ in range(LINHAS)]

def contar_vizinhos(grade, l, c):
    total = 0
    for dl in (-1, 0, 1):
        for dc in (-1, 0, 1):
            if dl == 0 and dc == 0:
                continue
            nl = l + dl
            nc = c + dc
            if 0 <= nl < len(grade) and 0 <= nc < len(grade[0]):
                total += grade[nl][nc]   # viva = 1, morta = 0, então somar conta os vivos
    return total