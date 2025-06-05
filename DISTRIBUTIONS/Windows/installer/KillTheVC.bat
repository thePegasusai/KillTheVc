@echo off
echo Starting Kill the VC...
echo.
echo Checking Python installation...

python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python is not installed or not in your PATH.
    echo Please install Python 3.7 or later from https://www.python.org/downloads/
    echo.
    echo Press any key to exit...
    pause >nul
    exit /b 1
)

echo Checking dependencies...
cd "%~dp0python"
python -m pip install -r ..\requirements.txt

echo.
echo Starting the game...
python game.py

if %errorlevel% neq 0 (
    echo.
    echo An error occurred while running the game.
    echo Please check that all dependencies are installed correctly.
    echo.
    echo Press any key to exit...
    pause >nul
    exit /b 1
)

exit /b 0
