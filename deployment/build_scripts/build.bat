@echo off
REM Main build script for Dental Practice Manager Windows Application
REM Ensures Windows 8+ compatibility and fast performance

cd /d "%~dp0..\.."

echo ================================================
echo Building Dental Practice Manager for Windows
echo ================================================

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ and try again
    pause
    exit /b 1
)

REM Check if required packages are installed
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

REM Run the build script
echo Starting build process...
python deployment\build_scripts\build_windows.py

if errorlevel 1 (
    echo BUILD FAILED!
    pause
    exit /b 1
) else (
    echo.
    echo ================================================
    echo BUILD SUCCESSFUL!
    echo ================================================
    echo.
    echo Your application is ready in the deployment folder:
    echo - deployment\ready_to_deploy\DentalPracticeManager\
    echo - Use launch.bat for optimal performance
    echo.
    echo Press any key to open the deployment folder...
    pause >nul
    explorer deployment\ready_to_deploy
)
