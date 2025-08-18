@echo off
REM Update deployment script for new dependencies (reportlab)
REM This script will install the new dependency and rebuild the application

cd /d "%~dp0"

echo ================================================
echo Updating Dental Practice Manager Build
echo ================================================
echo.
echo This will:
echo   1. Install new dependencies (reportlab for PDF export)
echo   2. Clean previous build
echo   3. Rebuild application with new features
echo   4. Test the updated build
echo.

choice /C YN /M "Do you want to proceed"
if errorlevel 2 goto :end

REM Step 1: Install new dependencies
echo.
echo ================================================
echo Step 1: Installing New Dependencies
echo ================================================
pip install --upgrade reportlab>=4.0.0
if errorlevel 1 (
    echo ERROR: Failed to install reportlab
    echo Please check your internet connection and try again
    pause
    goto :end
)

REM Step 2: Clean previous build
echo.
echo ================================================
echo Step 2: Cleaning Previous Build
echo ================================================
cd ..
if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"
if exist "dental_app.spec" del "dental_app.spec"
if exist "dental_app_debug.spec" del "dental_app_debug.spec"
echo Previous build cleaned.

REM Step 3: Rebuild with new dependencies
echo.
echo ================================================
echo Step 3: Rebuilding Application
echo ================================================
cd build_scripts
call build.bat
if errorlevel 1 (
    echo.
    echo BUILD FAILED! Trying fix script...
    call fix_build.bat
    if errorlevel 1 (
        echo UPDATE FAILED at build step!
        pause
        goto :end
    )
)

REM Step 4: Test the updated build
echo.
echo ================================================
echo Step 4: Testing Updated Build
echo ================================================
cd ..\tools
python test_windows_build.py
if errorlevel 1 (
    echo.
    echo Some tests failed. Check the build.
    choice /C YN /M "Continue anyway"
    if errorlevel 2 goto :end
)

REM Summary
echo.
echo ================================================
echo UPDATE COMPLETED SUCCESSFULLY!
echo ================================================
echo.
echo ✅ New features added:
echo    - PDF export functionality (reportlab)
echo    - Export dialogs updated
echo    - All dependencies included in build
echo.
echo 📁 Updated application: ..\ready_to_deploy\DentalPracticeManager\
echo 🚀 Run: launch.bat for best performance
echo.
echo The application now supports PDF export without external dependencies!
echo.

choice /C YN /M "Open the updated application folder"
if errorlevel 1 (
    explorer ..\ready_to_deploy\DentalPracticeManager
)

:end
echo.
echo Update script finished.
pause
