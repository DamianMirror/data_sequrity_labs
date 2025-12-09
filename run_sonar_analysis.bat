@echo off
REM SonarQube Analysis Script for Windows

echo ========================================
echo Running SonarQube Analysis
echo ========================================

REM Step 1: Run tests with coverage in XML format
echo.
echo [1/4] Running tests and generating coverage...
cd backend
pytest tests/ --cov=lab1_utils --cov=lab2_utils --cov=lab3_units --cov=lab_4_units --cov=lab5_utils --cov-report=xml --cov-report=html --junitxml=test-results.xml
cd ..

REM Step 2: Check if coverage.xml exists
if not exist "backend\coverage.xml" (
    echo ERROR: Coverage report not generated!
    exit /b 1
)

echo.
echo [2/4] Coverage report generated successfully!

REM Step 3: Run SonarScanner
echo.
echo [3/4] Running SonarScanner...
sonar-scanner.bat

REM Step 4: Done
echo.
echo [4/4] Analysis complete!
echo.
echo ========================================
echo SonarQube Results:
echo Open http://localhost:9000 in your browser
echo ========================================

pause