@echo off
REM SonarQube Analysis using Docker - Simple version without interactive input

echo ========================================
echo Running SonarQube Analysis with Docker
echo ========================================

REM Set your token here
set SONAR_TOKEN=sqa_e363103c50a795c39601e47ccea5b5ad58281c56

REM Step 1: Check if Docker is running
echo.
echo [1/5] Checking Docker...
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Docker is not installed or not running!
    pause
    exit /b 1
)
echo Docker is running!

REM Step 2: Start SonarQube server if not running
echo.
echo [2/5] Starting SonarQube server...
docker-compose -f docker-compose.sonarqube.yml up -d
timeout /t 10 /nobreak >nul
echo SonarQube server started!

REM Step 3: Run tests with coverage IN DOCKER (same paths as SonarQube!)
echo.
echo [3/5] Running tests and generating coverage in Docker...
docker run --rm ^
    -v "%cd%:/usr/src" ^
    -w /usr/src/backend ^
    python:3.11-slim ^
    bash -c "pip install -q pytest pytest-cov cryptography pandas numpy numba && pytest tests/ --cov=lab1_utils --cov=lab2_utils --cov=lab3_units --cov=lab_4_units --cov=lab5_utils --cov=utils --cov=algo_tests --cov-report=xml --cov-report=html --junitxml=test-results.xml"
if %errorlevel% neq 0 (
    echo WARNING: Some tests failed, but continuing with analysis...
)

REM Step 4: Check if coverage.xml exists
if not exist "backend\coverage.xml" (
    echo WARNING: Coverage report not generated!
    echo SonarQube will run without coverage data...
) else (
    echo Coverage report generated!
)

REM Step 5: Run SonarScanner using Docker
echo.
echo [4/5] Running SonarScanner using Docker with your token...
docker run --rm ^
    --network host ^
    -v "%cd%:/usr/src" ^
    sonarsource/sonar-scanner-cli ^
    -Dsonar.host.url=http://localhost:9000 ^
    -Dsonar.login=%SONAR_TOKEN%

REM Step 6: Done
echo.
echo [5/5] Analysis complete!
echo.
echo ========================================
echo SonarQube Results:
echo Open http://localhost:9000 in your browser
echo ========================================
echo.

pause
