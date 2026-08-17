# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['launch_biddinghero.py'],
    pathex=[],
    binaries=[],
    datas=[('biddinghero/templates', 'templates')],
    hiddenimports=['flask', 'requests', 'openpyxl', 'biddinghero', 'biddinghero.app_ui', 'biddinghero.api', 'biddinghero.grab_task'],
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
    a.binaries,
    a.datas,
    [],
    name='biddinghero',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch='arm64',
    codesign_identity=None,
    entitlements_file=None,
)
