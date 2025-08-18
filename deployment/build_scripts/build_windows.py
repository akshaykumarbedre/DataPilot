"""
Windows Application Builder for Dental Practice Management System
Creates optimized Windows executable with fast startup and Windows 8+ support.
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path


class WindowsAppBuilder:
    """Builder class for creating Windows application."""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent.parent
        self.deployment_root = Path(__file__).parent.parent
        self.build_dir = self.project_root / "build"
        self.dist_dir = self.project_root / "dist"
        self.spec_file = self.project_root / "dental_app.spec"
        
    def clean_build(self):
        """Clean previous build artifacts."""
        print("🧹 Cleaning previous build artifacts...")
        
        dirs_to_clean = [self.build_dir, self.dist_dir]
        files_to_clean = [self.spec_file]
        
        for dir_path in dirs_to_clean:
            if dir_path.exists():
                shutil.rmtree(dir_path)
                print(f"   Removed: {dir_path}")
        
        for file_path in files_to_clean:
            if file_path.exists():
                file_path.unlink()
                print(f"   Removed: {file_path}")
    
    def create_spec_file(self):
        """Create optimized PyInstaller spec file."""
        print("📝 Creating PyInstaller spec file...")
        
        spec_content = '''# -*- mode: python ; coding: utf-8 -*-

import sys
from pathlib import Path

# Project paths
project_root = Path(SPECPATH)
app_path = project_root / "app"

# Analysis configuration
a = Analysis(
    ['app.py'],
    pathex=[str(project_root)],
    binaries=[],
    datas=[
        # Include database files
        ('data/*.db', 'data'),
        # Include any resource files
        ('app/resources', 'app/resources'),
        ('app/icon/*.png', 'app/icon'),

    ],
    hiddenimports=[
        # Core Python modules (often missing in PyInstaller)
        'urllib',
        'urllib.parse',
        'urllib.request',
        'urllib.error',
        'urllib.response',
        'http',
        'http.client',
        'pathlib',
        'collections',
        'collections.abc',
        'functools',
        'itertools',
        'operator',
        'pickle',
        'json',
        'xml',
        'xml.etree',
        'xml.etree.ElementTree',
        'email',
        'email.mime',
        'calendar',
        'difflib',
        'inspect',
        
        # PySide6 modules
        'PySide6.QtCore',
        'PySide6.QtWidgets', 
        'PySide6.QtGui',
        'PySide6.QtSql',
        'PySide6.QtNetwork',
        
        # Application modules
        'app',
        'app.config',
        'app.main',
        'app.database',
        'app.database.database',
        'app.database.models',
        'app.services',
        'app.services.auth_service',
        'app.services.patient_service',
        'app.services.dental_service',
        'app.services.export_service',
        'app.ui',
        'app.ui.login_dialog',
        'app.ui.main_window',
        'app.ui.dashboard',
        'app.ui.patient_management',
        'app.ui.dental_chart',
        'app.ui.dialogs',
        'app.ui.dialogs.export_dialog',
        'app.utils',
        'app.utils.constants',
        
        # SQLite support
        'sqlite3',
        
        # PDF generation (reportlab)
        'reportlab',
        'reportlab.lib',
        'reportlab.lib.pagesizes',
        'reportlab.lib.styles',
        'reportlab.lib.colors',
        'reportlab.lib.units',
        'reportlab.platypus',
        'reportlab.platypus.tables',
        'reportlab.platypus.paragraph',
        'reportlab.platypus.doctemplate',
        'reportlab.pdfgen',
        'reportlab.pdfgen.canvas',
        
        # Python standard library essentials
        'logging',
        'logging.handlers',
        'threading',
        'queue',
        'datetime',
        'decimal',
        'hashlib',
        'hmac',
        'base64',
        'binascii',
        'struct',
        'array',
        'ctypes',
        'ctypes.util',
        'os',
        'sys',
        'platform',
        'subprocess',
        'shutil',
        'tempfile',
        'zipfile',
        'tarfile',
        'gzip',
        'locale',
        'gettext',
        'configparser',
        'argparse',
        'traceback',
        'warnings',
        'weakref',
        'copy',
        'types',
        'enum',
        'dataclasses',
        'typing',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # Only exclude modules we absolutely don't need
        'matplotlib',
        'numpy', 
        'pandas',
        'scipy',
        'tensorflow',
        'torch',
        'sklearn',
        'jupyter',
        'IPython',
        'notebook',
        'cv2',
        'PIL',
        'Pillow',
        'tkinter',
        'unittest.mock',
        'doctest',
        'pdb',
        'profile',
        'cProfile',
        'pip',
        'setuptools',
        'wheel',
        'distutils',
        'ftplib',
        'imaplib',
        'poplib',
        'smtplib',
        'telnetlib',
        'webbrowser',
        'Tkinter',
        'wx',
        'gtk',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

# Remove duplicates and optimize
pyz = PYZ(a.pure, a.zipped_data, cipher=None)

# Create executable
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='DentalPracticeManager',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,  # Compress executable
    console=False,  # No console window
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='app_icon.ico' if Path('app_icon.ico').exists() else None,
    version='version_info.txt' if Path('version_info.txt').exists() else None,
)

# Create distribution
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='DentalPracticeManager'
)
'''
        
        with open(self.spec_file, 'w', encoding='utf-8') as f:
            f.write(spec_content)
        
        print(f"   Created: {self.spec_file}")
    
    def create_version_info(self):
        """Create version information file for Windows executable."""
        print("📋 Creating version information...")
        
        version_content = '''# UTF-8
#
# For more details about fixed file info 'ffi' see:
# http://msdn.microsoft.com/en-us/library/ms646997.aspx
VSVersionInfo(
  ffi=FixedFileInfo(
    # filevers and prodvers should be always a tuple with four items: (1, 2, 3, 4)
    # Set not needed items to zero 0.
    filevers=(1,0,0,0),
    prodvers=(1,0,0,0),
    # Contains a bitmask that specifies the valid bits 'flags'r
    mask=0x3f,
    # Contains a bitmask that specifies the Boolean attributes of the file.
    flags=0x0,
    # The operating system for which this file was designed.
    # 0x4 - NT and there is no need to change it.
    OS=0x4,
    # The general type of file.
    # 0x1 - the file is an application.
    fileType=0x1,
    # The function of the file.
    # 0x0 - the function is not defined for this fileType
    subtype=0x0,
    # Creation date and time stamp.
    date=(0, 0)
    ),
  kids=[
    StringFileInfo(
      [
      StringTable(
        u'040904B0',
        [StringStruct(u'CompanyName', u'Dental Solutions'),
        StringStruct(u'FileDescription', u'Dental Practice Management System'),
        StringStruct(u'FileVersion', u'1.0.0.0'),
        StringStruct(u'InternalName', u'DentalPracticeManager'),
        StringStruct(u'LegalCopyright', u'Copyright (C) 2025 Dental Solutions'),
        StringStruct(u'OriginalFilename', u'DentalPracticeManager.exe'),
        StringStruct(u'ProductName', u'Dental Practice Manager'),
        StringStruct(u'ProductVersion', u'1.0.0.0')])
      ]), 
    VarFileInfo([VarStruct(u'Translation', [1033, 1200])])
  ]
)
'''
        
        version_file = self.project_root / "version_info.txt"
        with open(version_file, 'w', encoding='utf-8') as f:
            f.write(version_content)
        
        print(f"   Created: {version_file}")
    
    def build_executable(self):
        """Build the Windows executable."""
        print("🔨 Building Windows executable...")
        
        # Run PyInstaller with the spec file
        cmd = [
            sys.executable, '-m', 'PyInstaller',
            '--clean',
            '--noconfirm',
            str(self.spec_file)
        ]
        
        print(f"   Running: {' '.join(cmd)}")
        
        try:
            result = subprocess.run(
                cmd,
                cwd=self.project_root,
                capture_output=True,
                text=True,
                check=True
            )
            
            print("   Build completed successfully!")
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"   Build failed: {e}")
            print(f"   stdout: {e.stdout}")
            print(f"   stderr: {e.stderr}")
            return False
    
    def create_launcher_script(self):
        """Create optimized launcher script."""
        print("🚀 Creating launcher script...")
        
        launcher_content = '''@echo off
REM Dental Practice Manager Launcher
REM Optimized for Windows 8+ compatibility and fast startup

echo Starting Dental Practice Manager...

REM Set compatibility mode for Windows 8+
set __COMPAT_LAYER=WIN8RTM

REM Set high DPI awareness
set QT_AUTO_SCREEN_SCALE_FACTOR=1
set QT_SCALE_FACTOR=1

REM Set performance options
set QT_LOGGING_RULES=qt.qpa.gl=false

REM Launch application
start "Dental Practice Manager" /HIGH "DentalPracticeManager.exe"

REM Exit launcher
exit
'''
        
        launcher_file = self.dist_dir / "DentalPracticeManager" / "launch.bat"
        if launcher_file.parent.exists():
            with open(launcher_file, 'w', encoding='utf-8') as f:
                f.write(launcher_content)
            print(f"   Created: {launcher_file}")
    
    def post_build_optimization(self):
        """Perform post-build optimizations."""
        print("⚙️ Performing post-build optimizations...")
        
        exe_path = self.dist_dir / "DentalPracticeManager" / "DentalPracticeManager.exe"
        
        if exe_path.exists():
            # Create compatibility manifest
            manifest_content = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<assembly xmlns="urn:schemas-microsoft-com:asm.v1" manifestVersion="1.0">
  <assemblyIdentity
    version="1.0.0.0"
    processorArchitecture="*"
    name="DentalPracticeManager"
    type="win32"/>
  
  <!-- Windows 8+ compatibility -->
  <compatibility xmlns="urn:schemas-microsoft-com:compatibility.v1">
    <application>
      <supportedOS Id="{4a2f28e3-53b9-4441-ba9c-d69d4a4a6e38}"/>  <!-- Windows 10 -->
      <supportedOS Id="{1f676c76-80e1-4239-95bb-83d0f6d0da78}"/>  <!-- Windows 8.1 -->
      <supportedOS Id="{4a2f28e3-53b9-4441-ba9c-d69d4a4a6e38}"/>  <!-- Windows 8 -->
    </application>
  </compatibility>
  
  <!-- DPI awareness -->
  <application xmlns="urn:schemas-microsoft-com:asm.v3">
    <windowsSettings>
      <dpiAware xmlns="http://schemas.microsoft.com/SMI/2005/WindowsSettings">true</dpiAware>
      <dpiAwareness xmlns="http://schemas.microsoft.com/SMI/2016/WindowsSettings">PerMonitorV2</dpiAwareness>
    </windowsSettings>
  </application>
  
  <!-- Administrative privileges -->
  <trustInfo xmlns="urn:schemas-microsoft-com:asm.v2">
    <security>
      <requestedPrivileges xmlns="urn:schemas-microsoft-com:asm.v3">
        <requestedExecutionLevel level="asInvoker" uiAccess="false"/>
      </requestedPrivileges>
    </security>
  </trustInfo>
</assembly>'''
            
            manifest_file = exe_path.with_suffix('.exe.manifest')
            with open(manifest_file, 'w', encoding='utf-8') as f:
                f.write(manifest_content)
            
            print(f"   Created compatibility manifest: {manifest_file}")
    
    def copy_to_deployment(self):
        """Copy built application to deployment folder."""
        print("📁 Copying to deployment folder...")
        
        if (self.dist_dir / "DentalPracticeManager").exists():
            deployment_app_dir = self.deployment_root / "ready_to_deploy" / "DentalPracticeManager"
            
            # Create deployment directory
            deployment_app_dir.parent.mkdir(exist_ok=True)
            
            # Remove existing deployment if present
            if deployment_app_dir.exists():
                shutil.rmtree(deployment_app_dir)
            
            # Copy the built application
            shutil.copytree(
                self.dist_dir / "DentalPracticeManager",
                deployment_app_dir
            )
            
            print(f"   Copied application to: {deployment_app_dir}")
            return True
        
        return False
    
    def build(self):
        """Main build process."""
        print("🏗️ Building Windows Application for Dental Practice Manager")
        print("=" * 60)
        
        try:
            self.clean_build()
            self.create_version_info()
            self.create_spec_file()
            
            if self.build_executable():
                self.create_launcher_script()
                self.post_build_optimization()
                self.copy_to_deployment()
                
                print("=" * 60)
                print("✅ Build completed successfully!")
                print(f"📁 Application folder: {self.dist_dir / 'DentalPracticeManager'}")
                print(f"🚀 Executable: {self.dist_dir / 'DentalPracticeManager' / 'DentalPracticeManager.exe'}")
                print(f"📦 Deployment ready: {self.deployment_root / 'ready_to_deploy'}")
                print("\n🎯 Features included:")
                print("   ✓ Windows 8+ compatibility")
                print("   ✓ Fast startup optimization")
                print("   ✓ High DPI awareness")
                print("   ✓ Launcher script for optimal performance")
                
                return True
            else:
                print("❌ Build failed!")
                return False
                
        except Exception as e:
            print(f"❌ Build error: {e}")
            return False


if __name__ == "__main__":
    builder = WindowsAppBuilder()
    success = builder.build()
    sys.exit(0 if success else 1)
