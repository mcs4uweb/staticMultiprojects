@echo off
REM RockAuto Scraper Setup Script for Windows

echo ========================================
echo RockAuto Scraper Setup
echo ========================================
echo.

REM Check Python
echo Checking Python version...
python --version

if %errorlevel% neq 0 (
    echo Error: Python is not installed or not in PATH
    pause
    exit /b 1
)

echo.
echo Installing dependencies...
pip install -r requirements.txt

if %errorlevel% equ 0 (
    echo.
    echo Setup complete!
    echo.
    echo Quick Start:
    echo   1. Search for a part:
    echo      python rockauto_scraper.py --part "AC252709"
    echo.
    echo   2. Run examples:
    echo      python example_usage.py
    echo.
    echo   3. View help:
    echo      python rockauto_scraper.py --help
    echo.
) else (
    echo.
    echo Installation failed
    echo Try installing packages individually:
    echo   pip install selenium
    echo   pip install webdriver-manager
    echo   pip install beautifulsoup4
    echo   pip install requests
    echo.
)

pause