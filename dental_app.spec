# -*- mode: python ; coding: utf-8 -*-

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
        ('app/ui/resources/style.qss', 'app/ui/resources'),

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
