# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_submodules

a = Analysis(
    ['launcher.py'],
    pathex=["."],
    binaries=[],
    datas=[
         ("frontend/dist", "frontend/dist"),
         ("playwright-browsers", "playwright-browsers"),
    ],
    hiddenimports=[
         "backend.main",
    ] + collect_submodules("selenium") + collect_submodules("webdriver_manager"),
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
    name='LinkedIn Auto Commenter',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
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
    name='LinkedIn Auto Commenter',
)
