@echo off
REM Build installer using NSIS
REM Make sure NSIS is installed and in PATH

cd /d "%~dp0"

echo ================================================
echo Building Dental Practice Manager Installer
echo ================================================

REM Check if NSIS is available
makensis /VERSION >nul 2>&1
if errorlevel 1 (
    echo ERROR: NSIS is not installed or not in PATH
    echo Please install NSIS from https://nsis.sourceforge.io/
    echo and add it to your PATH
    pause
    exit /b 1
)

REM Check if the application has been built
if not exist "..\ready_to_deploy\DentalPracticeManager\DentalPracticeManager.exe" (
    echo ERROR: Application not found!
    echo Please build the application first using:
    echo   deployment\build_scripts\build.bat
    pause
    exit /b 1
)

REM Create LICENSE.txt if it doesn't exist
if not exist "LICENSE.txt" (
    echo Creating LICENSE.txt...
    echo MIT License > LICENSE.txt
    echo. >> LICENSE.txt
    echo Copyright ^(c^) 2025 Dental Solutions >> LICENSE.txt
    echo. >> LICENSE.txt
    echo Permission is hereby granted, free of charge, to any person obtaining a copy >> LICENSE.txt
    echo of this software and associated documentation files ^(the "Software"^), to deal >> LICENSE.txt
    echo in the Software without restriction, including without limitation the rights >> LICENSE.txt
    echo to use, copy, modify, merge, publish, distribute, sublicense, and/or sell >> LICENSE.txt
    echo copies of the Software, and to permit persons to whom the Software is >> LICENSE.txt
    echo furnished to do so, subject to the following conditions: >> LICENSE.txt
    echo. >> LICENSE.txt
    echo THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND. >> LICENSE.txt
)

REM Build installer
echo Building installer...
makensis installer.nsi

if errorlevel 1 (
    echo INSTALLER BUILD FAILED!
    pause
    exit /b 1
) else (
    echo.
    echo ================================================
    echo INSTALLER BUILD SUCCESSFUL!
    echo ================================================
    echo.
    echo Installer created: DentalPracticeManager_Setup.exe
    echo.
    echo You can now distribute this installer to end users.
    echo.
    pause
)
