import pandas as pd
import os

def lcg(seed: int, a: int, c: int, m: int, n: int):
    numbers = []
    x = seed
    for _ in range(n):
        x = (a * x + c) % m
        numbers.append(x)
    return numbers


def save_to_csv(numbers, filename: str = "./data/generated_numbers.csv"):
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    df = pd.DataFrame(numbers, columns=["number"])
    df.to_csv(filename, index=False)
