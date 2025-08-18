"""
Debug builder for troubleshooting Windows application issues.
Creates a console version to see error messages.
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path


class DebugWindowsAppBuilder:
    """Debug builder class for troubleshooting."""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent.parent
        self.deployment_root = Path(__file__).parent.parent
        self.build_dir = self.project_root / "build"
        self.dist_dir = self.project_root / "dist"
        self.spec_file = self.project_root / "dental_app_debug.spec"
        
    def clean_build(self):
        """Clean previous build artifacts."""
        print("🧹 Cleaning debug build artifacts...")
        
        dirs_to_clean = [self.build_dir, self.dist_dir]
        if self.spec_file.exists():
            self.spec_file.unlink()
            print(f"   Removed: {self.spec_file}")
        
        for dir_path in dirs_to_clean:
            if dir_path.exists():
                shutil.rmtree(dir_path)
                print(f"   Removed: {dir_path}")
    
    def create_debug_spec_file(self):
        """Create debug PyInstaller spec file with console output."""
        print("📝 Creating debug spec file...")
        
        spec_content = '''# -*- mode: python ; coding: utf-8 -*-
# DEBUG VERSION - Shows console output for troubleshooting

import sys
from pathlib import Path

# Project paths
project_root = Path(SPECPATH)
app_path = project_root / "app"

# Analysis configuration with extensive module inclusion
a = Analysis(
    ['app.py'],
    pathex=[str(project_root)],
    binaries=[],
    datas=[
        # Include database files
        ('data/*.db', 'data'),
        # Include any resource files
        ('app/resources', 'app/resources'),
        # Include application icon
         ('app/icon/*.png', 'app/icon'),
    ],
    hiddenimports=[
        # CRITICAL: Include ALL core Python modules
        'urllib',
        'urllib.parse', 
        'urllib.request',
        'urllib.error',
        'urllib.response',
        'http',
        'http.client',
        'http.server',
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
        
        # SQLite and database support
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
        'reportlab.graphics',
        'reportlab.graphics.shapes',
        
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
        'typing_extensions',
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
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=None)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='DentalPracticeManager_Debug',
    debug=True,  # Enable debug mode
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,  # Disable UPX for debugging
    console=True,  # ENABLE CONSOLE for error messages
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name='DentalPracticeManager_Debug'
)
'''
        
        with open(self.spec_file, 'w', encoding='utf-8') as f:
            f.write(spec_content)
        
        print(f"   Created: {self.spec_file}")
    
    def build_debug_executable(self):
        """Build the debug Windows executable."""
        print("🔨 Building debug Windows executable...")
        
        # Run PyInstaller with the debug spec file
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
            
            print("   Debug build completed successfully!")
            print("   You can now run the debug version to see console output")
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"   Debug build failed: {e}")
            print(f"   stdout: {e.stdout}")
            print(f"   stderr: {e.stderr}")
            return False
    
    def build(self):
        """Main debug build process."""
        print("🐛 Building DEBUG Windows Application")
        print("=" * 50)
        
        try:
            self.clean_build()
            self.create_debug_spec_file()
            
            if self.build_debug_executable():
                print("=" * 50)
                print("✅ Debug build completed successfully!")
                print(f"📁 Debug application: {self.dist_dir / 'DentalPracticeManager_Debug'}")
                print(f"🐛 Debug executable: {self.dist_dir / 'DentalPracticeManager_Debug' / 'DentalPracticeManager_Debug.exe'}")
                print("\n🎯 Debug features:")
                print("   ✓ Console output enabled")
                print("   ✓ All Python modules included")
                print("   ✓ Debug symbols preserved")
                print("   ✓ UPX compression disabled")
                print("\n💡 Run the debug executable to see detailed error messages!")
                
                return True
            else:
                print("❌ Debug build failed!")
                return False
                
        except Exception as e:
            print(f"❌ Debug build error: {e}")
            return False


if __name__ == "__main__":
    builder = DebugWindowsAppBuilder()
    success = builder.build()
    sys.exit(0 if success else 1)
