#!/bin/bash
# SonarQube Analysis Script for Linux/Mac

echo "========================================"
echo "Running SonarQube Analysis"
echo "========================================"

# Step 1: Run tests with coverage in XML format
echo ""
echo "[1/4] Running tests and generating coverage..."
cd backend
pytest tests/ --cov=lab1_utils --cov=lab2_utils --cov=lab3_units --cov=lab_4_units --cov=lab5_utils --cov-report=xml --cov-report=html --junitxml=test-results.xml
cd ..

# Step 2: Check if coverage.xml exists
if [ ! -f "backend/coverage.xml" ]; then
    echo "ERROR: Coverage report not generated!"
    exit 1
fi

echo ""
echo "[2/4] Coverage report generated successfully!"

# Step 3: Run SonarScanner
echo ""
echo "[3/4] Running SonarScanner..."
sonar-scanner

# Step 4: Done
echo ""
echo "[4/4] Analysis complete!"
echo ""
echo "========================================"
echo "SonarQube Results:"
echo "Open http://localhost:9000 in your browser"
echo "========================================"