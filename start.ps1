# Sequrity Labs Startup Script
Write-Host "Starting Sequrity Labs..." -ForegroundColor Green

# Перевіряємо чи встановлено Node.js
if (-not (Get-Command node -ErrorAction SilentlyContinue)) {
    Write-Host "Error: Node.js не знайдено. Будь ласка, встановіть Node.js." -ForegroundColor Red
    Read-Host "Натисніть Enter для виходу"
    exit 1
}

# Перевіряємо чи встановлено Python
if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Host "Error: Python не знайдено. Будь ласка, встановіть Python." -ForegroundColor Red
    Read-Host "Натисніть Enter для виходу"
    exit 1
}

# Функція для запуску процесів
function Start-Servers {
    Write-Host "Starting Backend Server..." -ForegroundColor Yellow
    $backend = Start-Process -FilePath "python" -ArgumentList "app.py" -WorkingDirectory "backend" -PassThru

    Start-Sleep -Seconds 3

    Write-Host "Starting Frontend Server..." -ForegroundColor Yellow
    $frontend = Start-Process -FilePath "cmd" -ArgumentList "/c", "npm run dev" -WorkingDirectory "frontend" -PassThru

    Start-Sleep -Seconds 5

    Write-Host "Opening browser..." -ForegroundColor Yellow
    Start-Process "http://localhost:5175"

    Write-Host "`nSequrity Labs запущено!" -ForegroundColor Green
    Write-Host "Backend: http://127.0.0.1:8001" -ForegroundColor Cyan
    Write-Host "Frontend: http://localhost:5175" -ForegroundColor Cyan
    Write-Host "`nНатисніть Ctrl+C щоб зупинити сервери." -ForegroundColor Yellow

    # Чекаємо натискання Ctrl+C
    try {
        while ($true) {
            Start-Sleep -Seconds 1
        }
    }
    finally {
        Write-Host "`nZупиняємо сервери..." -ForegroundColor Red
        if ($backend -and !$backend.HasExited) {
            Stop-Process -Id $backend.Id -Force
        }
        if ($frontend -and !$frontend.HasExited) {
            Stop-Process -Id $frontend.Id -Force
        }
    }
}

Start-Servers