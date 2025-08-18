@echo off
REM Debug build script for troubleshooting issues
REM Creates console version to see error messages

cd /d "%~dp0..\.."

echo ================================================
echo Building DEBUG Dental Practice Manager
echo ================================================

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ and try again
    pause
    exit /b 1
)

REM Check dependencies
echo Checking dependencies...
python -c "import PySide6" >nul 2>&1
if errorlevel 1 (
    echo Installing required packages...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo ERROR: Failed to install requirements
        pause
        exit /b 1
    )
)

REM Clean previous builds
echo Cleaning previous builds...
if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"

REM Run debug build
echo Starting DEBUG build process...
python deployment\build_scripts\build_debug.py

if errorlevel 1 (
    echo DEBUG BUILD FAILED!
    pause
    exit /b 1
) else (
    echo.
    echo ================================================
    echo DEBUG BUILD SUCCESSFUL!
    echo ================================================
    echo.
    echo Your debug application is ready:
    echo - dist\DentalPracticeManager_Debug\
    echo - Run DentalPracticeManager_Debug.exe to see console output
    echo.
    echo Press any key to open the debug folder...
    pause >nul
    explorer dist\DentalPracticeManager_Debug
)
