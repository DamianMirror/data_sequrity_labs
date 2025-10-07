from lab1_utils.gcd import gcd
import math

def cesaro_test(numbers: list[int]) -> tuple[float, float]:
    if len(numbers) < 2:
        return 0.0, 0.0

    pairs = zip(numbers[:-1], numbers[1:])
    coprime_count = sum(1 for a, b in pairs if gcd(a, b) == 1)
    total_pairs = len(numbers) - 1

    coprime_percent = coprime_count / total_pairs if total_pairs > 0 else 0.0

    print("coprime_percent:", coprime_percent)

    if coprime_percent <= 0:
        print("No coprime pairs found, returning 100% error")
        return coprime_percent, 100.0  # Максимальна похибка, якщо немає взаємно простих пар

    pi_estimate = math.sqrt(6 / coprime_percent)
    error = abs(math.pi - pi_estimate)
    relative_error = (error / math.pi) * 100

    print("relative_error:", relative_error)
    print("Returning tuple:", (coprime_percent, relative_error))

    return coprime_percent, relative_error
