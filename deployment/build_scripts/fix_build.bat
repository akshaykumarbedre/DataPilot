@echo off
REM Fix build script for urllib module issue
REM This script will clean and rebuild with correct module inclusions

cd /d "%~dp0..\.."

echo ================================================
echo Fixing Dental Practice Manager Windows Build
echo ================================================

echo Cleaning previous build...
if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"
if exist "dental_app.spec" del "dental_app.spec"
if exist "dental_app_debug.spec" del "dental_app_debug.spec"
if exist "*.manifest" del "*.manifest"

echo Installing/updating required packages...
pip install --upgrade pip
pip install --upgrade -r requirements.txt

echo.
echo Rebuilding with fixed configuration...
python deployment\build_scripts\build_windows.py

if errorlevel 1 (
    echo.
    echo BUILD FAILED! 
    echo Trying debug build to diagnose...
    python deployment\build_scripts\build_debug.py
    pause
    exit /b 1
) else (
    echo.
    echo ================================================
    echo BUILD COMPLETED SUCCESSFULLY!
    echo ================================================
    echo.
    echo Testing the application...
    python deployment\tools\test_windows_build.py
    
    echo.
    echo Your fixed application is ready in deployment\ready_to_deploy\
    echo Use launch.bat for optimal performance.
    echo.
    pause
)
