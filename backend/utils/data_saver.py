import pandas as pd
import os
from datetime import datetime
import json
import uuid

def save_lcg_results(numbers, lcg_params, coprime_percent, relative_error):
    """
    Зберігає результати генерації LCG в CSV файл з усіма даними.

    Args:
        numbers: Список згенерованих чисел
        lcg_params: Словник з параметрами LCG (m, a, c, x0, n)
        coprime_percent: Відсоток взаємно простих чисел
        relative_error: Відносна похибка оцінки π

    Returns:
        str: Шлях до створеного файла
    """
    # Створюємо папку data, якщо її немає
    os.makedirs("./data", exist_ok=True)

    # Генеруємо унікальне ім'я файла з датою, часом і UUID
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    unique_id = str(uuid.uuid4())[:8]  # Беремо перші 8 символів UUID
    filename = f"./data/lcg_results_{timestamp}_{unique_id}.csv"

    # Створюємо DataFrame з усіма даними
    data = []

    # Додаємо інформацію про параметри LCG
    data.append({
        'Type': 'Parameters',
        'Parameter': 'm (Модуль)',
        'Value': lcg_params.get('m', ''),
        'Description': f"2^{get_power_from_m(lcg_params.get('m', 0))} - 1"
    })
    data.append({
        'Type': 'Parameters',
        'Parameter': 'a (Множник)',
        'Value': lcg_params.get('a', ''),
        'Description': 'Параметр множника'
    })
    data.append({
        'Type': 'Parameters',
        'Parameter': 'c (Приріст)',
        'Value': lcg_params.get('c', ''),
        'Description': 'Параметр приросту'
    })
    data.append({
        'Type': 'Parameters',
        'Parameter': 'x0 (Початкове значення)',
        'Value': lcg_params.get('x0', ''),
        'Description': 'Seed для генератора'
    })
    data.append({
        'Type': 'Parameters',
        'Parameter': 'n (Кількість чисел)',
        'Value': lcg_params.get('n', ''),
        'Description': 'Загальна кількість згенерованих чисел'
    })

    # Додаємо порожній рядок
    data.append({
        'Type': '',
        'Parameter': '',
        'Value': '',
        'Description': ''
    })

    # Додаємо результати тестування
    data.append({
        'Type': 'Results',
        'Parameter': 'Coprime Percentage',
        'Value': f"{coprime_percent:.6f}",
        'Description': f"Відсоток взаємно простих пар: {coprime_percent * 100:.2f}%"
    })
    data.append({
        'Type': 'Results',
        'Parameter': 'Relative Error',
        'Value': f"{relative_error:.6f}",
        'Description': f"Відносна похибка оцінки π: {relative_error:.4f}%"
    })
    data.append({
        'Type': 'Results',
        'Parameter': 'Pi Estimate',
        'Value': f"{calculate_pi_estimate(coprime_percent):.6f}",
        'Description': f"Оцінка π через тест Чезаро"
    })

    # Додаємо порожній рядок
    data.append({
        'Type': '',
        'Parameter': '',
        'Value': '',
        'Description': ''
    })

    # Додаємо згенеровані числа
    for i, number in enumerate(numbers, 1):
        data.append({
            'Type': 'Generated Numbers',
            'Parameter': f'Number {i}',
            'Value': number,
            'Description': f'x_{i} = {number}'
        })

    # Створюємо DataFrame і зберігаємо
    df = pd.DataFrame(data)
    df.to_csv(filename, index=False, encoding='utf-8-sig')

    print(f"Результати збережено в файл: {filename}")
    return filename

def get_power_from_m(m):
    """
    Визначає степінь 2 для модуля виду 2^n - 1
    """
    if m <= 0:
        return 0

    # Перевіряємо, чи є m у формі 2^n - 1
    power = 1
    while (2**power - 1) < m:
        power += 1

    if (2**power - 1) == m:
        return power
    else:
        # Якщо не точно у формі 2^n - 1, повертаємо найближчий степінь
        return power - 1 if abs((2**(power-1) - 1) - m) < abs((2**power - 1) - m) else power

def calculate_pi_estimate(coprime_percent):
    """
    Розраховує оцінку π через тест Чезаро
    """
    import math
    if coprime_percent <= 0:
        return 0
    return math.sqrt(6 / coprime_percent)

def save_lcg_metadata(lcg_params, filename):
    """
    Зберігає метадані в JSON файл
    """
    metadata = {
        "timestamp": datetime.now().isoformat(),
        "lcg_parameters": lcg_params,
        "csv_file": filename,
        "description": "LCG Generator Results with Cesaro Test"
    }

    json_filename = filename.replace('.csv', '_metadata.json')
    with open(json_filename, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)

    return json_filename