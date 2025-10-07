@echo off
echo Starting Sequrity Labs...
echo.

REM Перевіряємо чи встановлено Node.js
where node >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Node.js не знайдено. Будь ласка, встановіть Node.js.
    pause
    exit /b 1
)

REM Перевіряємо чи встановлено Python
where python >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Python не знайдено. Будь ласка, встановіть Python.
    pause
    exit /b 1
)

echo Starting Backend Server...
start "Backend Server" cmd /k "cd backend && python app.py"

echo Waiting for backend to start...
timeout /t 3 /nobreak >nul

echo Starting Frontend Server...
start "Frontend Server" cmd /k "cd frontend && npm run dev"

echo Waiting for frontend to start...
timeout /t 5 /nobreak >nul

echo Opening browser...
start http://localhost:5175

echo.
echo Sequrity Labs запущено!
echo Backend: http://127.0.0.1:8001
echo Frontend: http://localhost:5175
echo.
echo Закрийте цю консоль щоб зупинити всі сервери.
pause