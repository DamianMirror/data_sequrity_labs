# SonarQube Setup Guide for Security Labs

## 📋 Що таке SonarQube?

SonarQube - це платформа для continuous inspection якості коду, яка:
- Виявляє bugs та vulnerabilities
- Знаходить code smells
- Аналізує test coverage
- Перевіряє дублювання коду
- Забезпечує security аналіз

## 🚀 Швидкий старт

### Варіант 1: Docker (Рекомендовано)

#### 1. Запустити SonarQube сервер:
```bash
docker-compose -f docker-compose.sonarqube.yml up -d
```

#### 2. Дочекатися запуску (1-2 хвилини):
```bash
docker logs -f security-labs-sonarqube
```

#### 3. Відкрити SonarQube:
- URL: http://localhost:9000
- Login: `admin`
- Password: `admin` (змініть при першому вході!)

#### 4. Створити токен:
1. Увійдіть як admin
2. Перейдіть: My Account → Security → Generate Tokens
3. Name: `security-labs`
4. Type: `Project Analysis Token`
5. Збережіть згенерований токен!

#### 5. Запустити аналіз:
```bash
# Windows
run_sonar_analysis.bat

# Linux/Mac
chmod +x run_sonar_analysis.sh
./run_sonar_analysis.sh
```

---

### Варіант 2: Встановлення SonarScanner локально

#### 1. Завантажити SonarScanner:
- Windows: https://binaries.sonarsource.com/Distribution/sonar-scanner-cli/sonar-scanner-cli-4.8.0.2856-windows.zip
- Linux: https://binaries.sonarsource.com/Distribution/sonar-scanner-cli/sonar-scanner-cli-4.8.0.2856-linux.zip
- Mac: https://binaries.sonarsource.com/Distribution/sonar-scanner-cli/sonar-scanner-cli-4.8.0.2856-macosx.zip

#### 2. Розпакувати та додати до PATH:
```bash
# Windows (додайте до системних змінних)
C:\sonar-scanner\bin

# Linux/Mac (додайте до ~/.bashrc або ~/.zshrc)
export PATH="$PATH:/path/to/sonar-scanner/bin"
```

#### 3. Перевірити встановлення:
```bash
sonar-scanner --version
```

---

## 📊 Запуск аналізу

### Автоматичний запуск:
```bash
# Windows
run_sonar_analysis.bat

# Linux/Mac
./run_sonar_analysis.sh
```

### Ручний запуск:

#### Крок 1: Запустити тести з coverage:
```bash
cd backend
pytest tests/ --cov=lab1_utils --cov=lab2_utils --cov=lab3_units --cov=lab_4_units --cov=lab5_utils --cov-report=xml
cd ..
```

#### Крок 2: Запустити SonarScanner:
```bash
sonar-scanner \
  -Dsonar.projectKey=security-labs \
  -Dsonar.sources=. \
  -Dsonar.host.url=http://localhost:9000 \
  -Dsonar.login=YOUR_TOKEN_HERE
```

---

## 🔧 Конфігурація

### Файли конфігурації:

1. **sonar-project.properties** - Основна конфігурація проекту
2. **backend/.coveragerc** - Налаштування coverage
3. **docker-compose.sonarqube.yml** - Docker конфігурація

### Налаштування токена:

Створіть файл `sonar-scanner.properties` у домашній директорії:
```properties
sonar.host.url=http://localhost:9000
sonar.login=YOUR_TOKEN_HERE
```

---

## 📈 Метрики SonarQube

Після аналізу ви побачите:

### Quality Gate:
- ✅ **Passed** - код відповідає стандартам якості
- ❌ **Failed** - потрібні покращення

### Основні метрики:
- **Bugs** - помилки в коді
- **Vulnerabilities** - безпекові вразливості
- **Code Smells** - підозрілі паттерни коду
- **Coverage** - покриття тестами
- **Duplications** - дубльований код
- **Complexity** - цикломатична складність

### Рівні:
- **Blocker** 🔴 - критичні проблеми
- **Critical** 🟠 - важливі проблеми
- **Major** 🟡 - серйозні проблеми
- **Minor** 🔵 - незначні проблеми
- **Info** ⚪ - інформаційні повідомлення

---

## 🎯 Інтеграція в CI/CD

### GitHub Actions:
```yaml
name: SonarQube Analysis

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  sonarqube:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2

      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.11

      - name: Install dependencies
        run: |
          cd backend
          pip install -r requirements.txt

      - name: Run tests with coverage
        run: |
          cd backend
          pytest tests/ --cov --cov-report=xml

      - name: SonarQube Scan
        uses: sonarsource/sonarqube-scan-action@master
        env:
          SONAR_TOKEN: ${{ secrets.SONAR_TOKEN }}
          SONAR_HOST_URL: ${{ secrets.SONAR_HOST_URL }}
```

---

## 🛠️ Корисні команди

### Управління Docker:
```bash
# Запуск
docker-compose -f docker-compose.sonarqube.yml up -d

# Зупинка
docker-compose -f docker-compose.sonarqube.yml down

# Переглянути логи
docker logs security-labs-sonarqube

# Перезапуск
docker-compose -f docker-compose.sonarqube.yml restart
```

### Очистка даних:
```bash
# Видалити контейнер та дані
docker-compose -f docker-compose.sonarqube.yml down -v

# Очистити кеш SonarQube
rm -rf .scannerwork
```

---

## 🐛 Troubleshooting

### Проблема: SonarQube не запускається
**Рішення:** Збільште пам'ять для Docker:
- Docker Desktop → Settings → Resources
- Memory: мінімум 4GB

### Проблема: "coverage.xml not found"
**Рішення:** Запустіть тести перед аналізом:
```bash
cd backend
pytest tests/ --cov --cov-report=xml
```

### Проблема: "Unauthorized" помилка
**Рішення:** Перевірте токен доступу:
1. Регенеруйте токен в SonarQube UI
2. Оновіть його в команді sonar-scanner

---

## 📚 Додаткові ресурси

- [SonarQube Documentation](https://docs.sonarqube.org/)
- [SonarQube Python Plugin](https://docs.sonarqube.org/latest/analysis/languages/python/)
- [Quality Gates](https://docs.sonarqube.org/latest/user-guide/quality-gates/)
- [Security Rules](https://rules.sonarsource.com/python/type/Security%20Hotspot)

---

## 📊 Очікувані результати

Для Security Labs проекту очікуємо:

- **Coverage**: 70-90% (поточно ~78%)
- **Bugs**: < 5
- **Vulnerabilities**: 0 (критично для security проекту!)
- **Code Smells**: < 20
- **Duplications**: < 3%
- **Maintainability Rating**: A або B

---

## 🎓 Best Practices

1. **Запускайте аналіз регулярно** - перед кожним commit
2. **Виправляйте Blockers та Critical** - негайно
3. **Слідкуйте за Security Hotspots** - особливо важливо для crypto коду
4. **Підтримуйте coverage > 70%** - додавайте тести для нового коду
5. **Переглядайте Code Smells** - покращуйте якість коду

---

## ✅ Чеклист після встановлення

- [ ] SonarQube сервер запущений і доступний на localhost:9000
- [ ] Створений токен доступу
- [ ] Запущений перший аналіз
- [ ] Переглянуті результати в UI
- [ ] Налаштовані Quality Gates
- [ ] Додано в CI/CD (опціонально)