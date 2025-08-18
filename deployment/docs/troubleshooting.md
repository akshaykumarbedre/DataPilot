# Troubleshooting Guide - Dental Practice Manager

This guide helps resolve common issues during building and running the Windows application.

## 🔧 Build Issues

### "No module named 'urllib'" Error

**Symptoms:**
```
ModuleNotFoundError: No module named 'urllib'
```

**Causes:**
- PyInstaller incorrectly excluded urllib module
- Missing core Python modules in spec file

**Solutions:**
1. **Quick Fix:**
   ```cmd
   cd deployment\build_scripts
   fix_build.bat
   ```

2. **Manual Fix:**
   - Edit the spec file to include urllib in hiddenimports
   - Remove urllib from excludes list
   - Rebuild application

3. **Debug Approach:**
   ```cmd
   cd deployment\build_scripts
   build_debug.bat
   ```

### PyInstaller Build Fails

**Symptoms:**
- Build process terminates with errors
- Missing dependencies
- Import errors during build

**Solutions:**
1. **Check Python Installation:**
   ```cmd
   python --version
   pip --version
   ```

2. **Update Dependencies:**
   ```cmd
   pip install --upgrade pip
   pip install --upgrade -r requirements.txt
   ```

3. **Clean Build:**
   ```cmd
   # Delete build and dist folders
   rmdir /s /q build
   rmdir /s /q dist
   # Rebuild
   python deployment\build_scripts\build_windows.py
   ```

### Missing PySide6 Dependencies

**Symptoms:**
- No Qt DLL files in dist folder
- Application won't start due to missing Qt

**Solutions:**
1. **Reinstall PySide6:**
   ```cmd
   pip uninstall PySide6
   pip install PySide6>=6.5.0
   ```

2. **Check Qt Installation:**
   ```cmd
   python -c "from PySide6.QtWidgets import QApplication; print('PySide6 OK')"
   ```

### Missing reportlab Dependencies

**Symptoms:**
```
PDF export not available. Please install reportlab: pip install reportlab
```

**Solutions:**
1. **Use Update Script:**
   ```cmd
   cd deployment\build_scripts
   update_build.bat
   ```

2. **Manual Installation:**
   ```cmd
   pip install reportlab>=4.0.0
   # Then rebuild
   python deployment\build_scripts\build_windows.py
   ```

3. **Verify Installation:**
   ```cmd
   python -c "import reportlab; print('ReportLab OK')"
   ```

## 🚀 Runtime Issues

### Application Won't Start

**Symptoms:**
- No window appears
- Process starts but terminates immediately
- No error messages in windowed mode

**Solutions:**
1. **Use Debug Version:**
   ```cmd
   cd deployment\build_scripts
   build_debug.bat
   # Run debug executable to see console output
   ```

2. **Check Dependencies:**
   ```cmd
   # Verify all DLL files are present
   python deployment\tools\test_windows_build.py
   ```

3. **Run with Console:**
   - Use debug build or modify spec file to enable console
   - Check for detailed error messages

### Slow Application Startup

**Symptoms:**
- Long delay before application window appears
- High disk activity during startup

**Solutions:**
1. **Use Optimized Launcher:**
   ```cmd
   # Instead of DentalPracticeManager.exe, use:
   launch.bat
   ```

2. **Antivirus Exclusions:**
   - Add application folder to antivirus exclusions
   - Exclude from real-time scanning

3. **Storage Optimization:**
   - Move application to SSD if available
   - Ensure sufficient free disk space

### Database Connection Errors

**Symptoms:**
```
Database Error: Failed to initialize database
```

**Solutions:**
1. **Check File Permissions:**
   - Ensure write access to application folder
   - Run as administrator if necessary

2. **Verify Database Files:**
   - Check if `data/dental_practice.db` exists
   - Verify file isn't corrupted

3. **Path Issues:**
   - Ensure relative paths work from application directory
   - Check working directory

### Display and DPI Issues

**Symptoms:**
- Blurry text on high-DPI displays
- Incorrect window sizing
- UI elements overlapping

**Solutions:**
1. **Windows Display Settings:**
   - Right-click application → Properties → Compatibility
   - Check "Override high DPI scaling behavior"

2. **Environment Variables:**
   ```cmd
   set QT_SCALE_FACTOR=1
   set QT_AUTO_SCREEN_SCALE_FACTOR=1
   DentalPracticeManager.exe
   ```

3. **Graphics Issues:**
   ```cmd
   set QT_OPENGL=software
   DentalPracticeManager.exe
   ```

## 🛠️ Development Issues

### Import Errors in Source Code

**Symptoms:**
- ModuleNotFoundError during development
- Missing application modules

**Solutions:**
1. **Check Python Path:**
   ```cmd
   # From project root
   python -c "import app.main; print('Import OK')"
   ```

2. **Virtual Environment:**
   ```cmd
   # Create virtual environment
   python -m venv venv
   venv\Scripts\activate
   pip install -r requirements.txt
   ```

### PySide6 Installation Issues

**Symptoms:**
- Cannot import PySide6
- Qt platform plugin errors

**Solutions:**
1. **Clean Installation:**
   ```cmd
   pip uninstall PySide6 PySide6-Essentials PySide6-Addons
   pip install PySide6
   ```

2. **Platform Plugins:**
   ```cmd
   # Check Qt platform plugins
   python -c "from PySide6.QtWidgets import QApplication; app = QApplication([])"
   ```

## 🖥️ System-Specific Issues

### Windows 8 Compatibility

**Symptoms:**
- Application doesn't start on Windows 8
- Missing API errors

**Solutions:**
1. **Compatibility Mode:**
   - Right-click executable → Properties → Compatibility
   - Select "Windows 8" compatibility mode

2. **Check Manifest:**
   - Verify `DentalPracticeManager.exe.manifest` exists
   - Contains Windows 8 compatibility declarations

### Antivirus False Positives

**Symptoms:**
- Antivirus blocks or deletes executable
- "Potentially unwanted program" warnings

**Solutions:**
1. **Whitelist Application:**
   - Add to antivirus exceptions
   - Exclude entire application folder

2. **Code Signing:**
   - Obtain code signing certificate
   - Sign the executable

3. **Submit to Vendors:**
   - Submit to antivirus vendors for analysis
   - Request whitelisting

### Performance on Older Hardware

**Symptoms:**
- Slow application performance
- High CPU usage
- Memory issues

**Solutions:**
1. **Graphics Settings:**
   ```cmd
   set QT_OPENGL=software
   set QT_QUICK_BACKEND=software
   DentalPracticeManager.exe
   ```

2. **Reduce Visual Effects:**
   - Disable Windows visual effects
   - Close unnecessary programs

3. **Memory Optimization:**
   - Ensure sufficient RAM
   - Close other applications

## 📝 Diagnostic Tools

### Build Diagnostics

```cmd
# Test build integrity
python deployment\tools\test_windows_build.py

# Check dependencies
python -c "import sys; print('\n'.join(sys.modules.keys()))"

# Verify PyInstaller
python -m PyInstaller --version
```

### Runtime Diagnostics

```cmd
# Check Qt installation
python -c "from PySide6.QtWidgets import QApplication; print('Qt OK')"

# Test database access
python -c "import sqlite3; print('SQLite OK')"

# Check application imports
python -c "from app.main import main; print('App imports OK')"
```

### System Information

```cmd
# Python version and path
python --version
where python

# System info
systeminfo | findstr /B /C:"OS Name" /C:"OS Version"

# Memory info
wmic computersystem get TotalPhysicalMemory
```

## 🔍 Log Analysis

### Application Logs

Check logs in:
- `logs/dental_app.log`
- Console output (debug build)
- Windows Event Viewer

### Build Logs

PyInstaller logs show:
- Missing modules
- Import errors
- Dependency issues

### Common Log Patterns

```
ERROR: Failed to import module 'xyz'
```
→ Add to hiddenimports in spec file

```
WARNING: lib not found: xyz.dll
```
→ Include binary in spec file or install missing runtime

```
ModuleNotFoundError: No module named 'abc'
```
→ Add to hiddenimports, check excludes list

## 📞 Getting Help

### Self-Diagnosis Steps
1. Run `test_windows_build.py`
2. Build debug version
3. Check console output
4. Review error logs
5. Test on clean system

### Information to Collect
- Windows version
- Python version
- Error messages
- Build logs
- System specifications

### Common Solutions Summary
- Use `fix_build.bat` for module issues
- Use debug build for troubleshooting
- Add antivirus exclusions
- Check file permissions
- Verify system requirements

---

*For additional support, run the diagnostic tools and review the error logs.*
