@echo off
REM Master deployment script for Dental Practice Manager
REM Builds, tests, and packages the complete Windows application

cd /d "%~dp0"

echo ================================================
echo Dental Practice Manager - Complete Deployment
echo ================================================

echo.
echo This script will:
echo   1. Build the Windows application
echo   2. Test the build
echo   3. Create distribution packages
echo   4. Optionally create installer
echo.

choice /C YN /M "Do you want to proceed"
if errorlevel 2 goto :end

REM Step 1: Build the application
echo.
echo ================================================
echo Step 1: Building Application
echo ================================================
call build_scripts\build.bat
if errorlevel 1 (
    echo.
    echo BUILD FAILED! Trying fix script...
    call build_scripts\fix_build.bat
    if errorlevel 1 (
        echo DEPLOYMENT FAILED at build step!
        pause
        goto :end
    )
)

REM Step 2: Test the build
echo.
echo ================================================
echo Step 2: Testing Build
echo ================================================
python tools\test_windows_build.py
if errorlevel 1 (
    echo.
    echo TESTS FAILED! Check the application build.
    choice /C YN /M "Continue anyway"
    if errorlevel 2 goto :end
)

REM Step 3: Create packages
echo.
echo ================================================
echo Step 3: Creating Distribution Packages
echo ================================================
python tools\create_packages.py
if errorlevel 1 (
    echo.
    echo PACKAGING FAILED!
    choice /C YN /M "Continue anyway"
    if errorlevel 2 goto :end
)

REM Step 4: Optional installer
echo.
echo ================================================
echo Step 4: Create Professional Installer (Optional)
echo ================================================
choice /C YN /M "Do you want to create a professional installer"
if errorlevel 1 (
    call installers\build_installer.bat
)

REM Summary
echo.
echo ================================================
echo DEPLOYMENT COMPLETED SUCCESSFULLY!
echo ================================================
echo.
echo 📁 Ready to deploy: ready_to_deploy\DentalPracticeManager\
echo 📦 Distribution packages: packages\
echo 🚀 Installer: installers\DentalPracticeManager_Setup.exe (if created)
echo.
echo Your application is ready for distribution!
echo.

choice /C YN /M "Open deployment folder"
if errorlevel 1 (
    explorer ready_to_deploy
)

:end
echo.
echo Deployment script finished.
pause
