@echo off

REM Change to the deployment directory
cd deployment

REM Activate conda environment
call conda activate dental

REM Run the build script
python build_scripts/build_windows.py

REM Compile the installer
"C:\Program Files (x86)\NSIS\makensis.exe" installers/installer.nsi

echo.
echo Build and packaging complete.
pause