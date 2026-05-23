@echo off
REM CryptoBlock Startup Script

echo.
echo ============================================================
echo CryptoBlock - Crypto Trading Platform
echo ============================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH
    pause
    exit /b 1
)

REM Check if MongoDB is running
tasklist | findstr /I "mongod" >nul 2>&1
if errorlevel 1 (
    echo [WARNING] MongoDB is not running
    echo Please start MongoDB before running the app
    echo.
    echo To start MongoDB:
    echo   1. Open Command Prompt as Administrator
    echo   2. Run: mongod
    echo.
    pause
    exit /b 1
)

echo [OK] MongoDB is running
echo.

REM Check if dependencies are installed
echo [INFO] Checking dependencies...
pip show flask >nul 2>&1
if errorlevel 1 (
    echo [INFO] Installing dependencies...
    pip install -r requirements.txt
)

echo.
echo ============================================================
echo Starting CryptoBlock App...
echo ============================================================
echo.
echo The app will be available at: http://localhost:5000
echo Press Ctrl+C to stop the server
echo.

REM Run the app
python app.py

pause
