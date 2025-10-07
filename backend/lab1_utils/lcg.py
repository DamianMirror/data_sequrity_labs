def lcg(seed: int, a: int, c: int, m: int, n: int):
    """Лінійний конгруентний генератор"""
    numbers = []
    x = seed
    for _ in range(n):
        x = (a * x + c) % m
        numbers.append(x)
    return numbers
