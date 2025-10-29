import numpy as np

def lcg(seed: int, a: int, c: int, m: int, n: int):
    numbers = np.empty(n, dtype=np.int64)
    x = seed
    for i in range(n):
        x = (a * x + c) % m
        numbers[i] = x
    return numbers.tolist()

