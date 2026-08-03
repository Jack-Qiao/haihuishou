# -*- mode: python ; coding: utf-8 -*-
# 在 biddingHero 项目目录执行：pyinstaller biddinghero.spec
# 打包完成后，可执行文件在 dist/biddinghero（macOS/Linux）或 dist/biddinghero.exe（Windows）

import os

project_root = os.path.dirname(os.path.abspath(SPEC))
biddinghero_pkg = os.path.join(project_root, 'biddinghero')
templates_src = os.path.join(biddinghero_pkg, 'templates')

datas = [(templates_src, 'templates')]

a = Analysis(
    [os.path.join(project_root, 'launch_biddinghero.py')],
    pathex=[project_root],
    datas=datas,
    hiddenimports=[
        'flask',
        'requests',
        'biddinghero',
        'biddinghero.app_ui',
        'biddinghero.api',
        'biddinghero.__init__',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
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
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
