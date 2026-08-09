# -*- mode: python ; coding: utf-8 -*-
# 在 biddingHero 项目目录执行：
#   .build-venv/bin/pyinstaller biddinghero.spec
# 打包产物：dist/biddinghero —— universal2（同时支持 Apple Silicon 与 Intel Mac）
#
# 注意：必须用 universal2 版 Python（python.org 安装的 3.x 即为 universal2）创建构建 venv，
# 否则 target_arch='universal2' 无法交叉收集两侧架构。

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
    upx=False,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch='universal2',
    codesign_identity=None,
    entitlements_file=None,
)
