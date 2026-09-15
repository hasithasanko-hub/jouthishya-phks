# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_submodules

hiddenimports = collect_submodules('webview')

a = Analysis(
    ['desktop.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('app', 'app'),
        ('commercial_config.json', '.'),
        ('installer/HelaJyotishya.ico', 'installer'),
    ],
    hiddenimports=hiddenimports + [
        'swisseph', 'tkinter',
        'sqlite3', '_sqlite3',
        'http.server', 'urllib.parse', 'mimetypes', 'traceback',
        'threading', 'hashlib', 'datetime', 'pathlib', 'json', 'os'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=1,
)
pyz = PYZ(a.pure)
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='HelaJyotishya',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='installer\\HelaJyotishya.ico',
)
