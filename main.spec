# -*- mode: python ; coding: utf-8 -*-
# NOBARO — PyInstaller spec.
# Build with:  pyinstaller main.spec
# Output:      dist/nobaro/nobaro.exe  (windowed, icon = icon.ico from public/logo.png)


import os

SPEC_DIR = os.path.dirname(os.path.abspath(SPEC))

a = Analysis(
    ['main.py'],
    pathex=[SPEC_DIR],
    binaries=[],
    datas=[
        ('public/logo.png', 'public'),
        ('public/logo_512.png', 'public'),
        ('public/logo_256.png', 'public'),
        ('icon.ico', '.'),
    ],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='nobaro',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    icon='icon.ico',
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='nobaro',
)
