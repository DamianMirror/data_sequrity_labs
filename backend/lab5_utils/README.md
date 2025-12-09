# Lab 5: Digital Signature Standard (DSS)

Реалізація цифрового підпису за стандартом DSS з використанням алгоритму DSA (Digital Signature Algorithm).

## Функціональність

### 1. Генерація ключів DSA
- Підтримка розмірів ключів: 1024, 2048, 3072 біт
- Генерація пари ключів (приватний та публічний)
- Збереження ключів у форматі PEM
- Можливість захисту приватного ключа паролем

### 2. Підпис рядків
- Створення цифрового підпису для текстових повідомлень
- Використання SHA-256 для хешування
- Підпис у шістнадцятковому форматі

### 3. Перевірка підпису рядків
- Верифікація цифрового підпису
- Перевірка автентичності та цілісності повідомлення

### 4. Підпис файлів
- Створення цифрового підпису для файлів будь-якого розміру
- Автоматичне збереження підпису у файл .sig
- Підпис зберігається у шістнадцятковому форматі

### 5. Перевірка підпису файлів
- Верифікація цифрового підпису файлу
- Завантаження підпису з .sig файлу
- Перевірка на підробку або зміну файлу

## Структура файлів

```
lab5_utils/
├── __init__.py          # Package initialization
├── dss_crypto.py        # Main DSS implementation
└── README.md            # This file
```

## API Endpoints

### POST /lab5/generate-keys/
Генерація пари DSA ключів

**Request:**
```json
{
  "key_size": 2048
}
```

**Response:**
```json
{
  "success": true,
  "key_size": 2048,
  "private_key_pem": "-----BEGIN PRIVATE KEY-----\n...",
  "public_key_pem": "-----BEGIN PUBLIC KEY-----\n...",
  "key_info": {
    "key_type": "Private Key",
    "key_size": 2048,
    "p_bits": 2048,
    "q_bits": 256,
    "g_bits": 2048
  }
}
```

### POST /lab5/sign-string/
Створення підпису для рядка

**Request (FormData):**
- `message`: текст для підпису
- `private_key_pem`: приватний ключ у форматі PEM

**Response:**
```json
{
  "success": true,
  "message": "Hello, World!",
  "signature_hex": "3045022100...",
  "signature_base64": "MEUCIQD...",
  "signature_length": 64
}
```

### POST /lab5/verify-string/
Перевірка підпису рядка

**Request (FormData):**
- `message`: оригінальний текст
- `signature_hex`: підпис у hex форматі
- `public_key_pem`: публічний ключ у форматі PEM

**Response:**
```json
{
  "success": true,
  "message": "Hello, World!",
  "is_valid": true,
  "verification_message": "Signature is valid!"
}
```

### POST /lab5/sign-file/
Створення підпису для файлу

**Request (FormData):**
- `file`: файл для підпису
- `private_key_pem`: приватний ключ у форматі PEM

**Response:**
```json
{
  "success": true,
  "filename": "document.pdf",
  "file_size": 12345,
  "signature_hex": "3045022100...",
  "signature_base64": "MEUCIQD...",
  "signature_length": 64
}
```

### POST /lab5/verify-file/
Перевірка підпису файлу

**Request (FormData):**
- `file`: файл для перевірки
- `signature_file`: файл підпису (.sig)
- `public_key_pem`: публічний ключ у форматі PEM

**Response:**
```json
{
  "success": true,
  "filename": "document.pdf",
  "signature_filename": "document.pdf.sig",
  "file_size": 12345,
  "is_valid": true,
  "verification_message": "File signature is valid!"
}
```

## Використання (Python)

```python
from lab5_utils.dss_crypto import (
    generate_dsa_keys,
    save_private_key,
    save_public_key,
    sign_string,
    verify_string_signature,
    sign_file,
    verify_file_signature,
    save_signature,
    load_signature
)

# Генерація ключів
private_key, public_key = generate_dsa_keys(key_size=2048)

# Збереження ключів
save_private_key(private_key, 'private.pem')
save_public_key(public_key, 'public.pem')

# Підпис рядка
message = "Important message"
signature = sign_string(message, private_key)

# Перевірка підпису рядка
is_valid = verify_string_signature(message, signature, public_key)
print(f"Signature valid: {is_valid}")

# Підпис файлу
file_signature = sign_file('document.pdf', private_key)
save_signature(file_signature, 'document.pdf.sig')

# Перевірка підпису файлу
loaded_sig = load_signature('document.pdf.sig')
is_valid = verify_file_signature('document.pdf', loaded_sig, public_key)
print(f"File signature valid: {is_valid}")
```

## Безпека

- **Приватний ключ**: Зберігайте приватний ключ у безпечному місці
- **Передача ключів**: Не передавайте приватний ключ через небезпечні канали
- **Хешування**: Використовується SHA-256 для хешування повідомлень
- **Захист паролем**: Опціонально можна захистити приватний ключ паролем

## Вимоги

- Python 3.7+
- cryptography >= 3.0

## Встановлення залежностей

```bash
pip install cryptography
```

## Тестування

Запустіть тестовий скрипт:

```bash
python lab5_utils/dss_crypto.py
```

Це виконає базові тести:
- Генерацію ключів
- Підпис і перевірку рядка
- Підпис і перевірку файлу
- Збереження і завантаження підпису

## Стандарти

Ця реалізація відповідає стандарту DSS (Digital Signature Standard) FIPS 186-4 та використовує:
- DSA (Digital Signature Algorithm)
- SHA-256 для хешування
- Формат PEM для зберігання ключів
- Шістнадцятковий формат для підписів