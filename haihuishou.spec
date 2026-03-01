# -*- mode: python ; coding: utf-8 -*-
# 在项目根目录（codingAi）执行：pyinstaller haihuishou.spec
# 打包完成后，可执行文件在 dist/manualOrderGrabTool（macOS/Linux）或 dist/manualOrderGrabTool.exe（Windows）

import os

project_root = os.path.dirname(os.path.abspath(SPEC))
haihuishou_dir = os.path.join(project_root, 'haihuishou')
templates_src = os.path.join(haihuishou_dir, 'templates')

# 把 haihuishou/templates 打包到 bundle 根目录的 templates
datas = [(templates_src, 'templates')]

a = Analysis(
    [os.path.join(project_root, 'launch_haihuishou.py')],
    pathex=[project_root],
    datas=datas,
    hiddenimports=[
        'flask',
        'requests',
        'haihuishou',
        'haihuishou.app_ui',
        'haihuishou.api',
        'haihuishou.grab_tool',
        'haihuishou.__init__',
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
    name='manualOrderGrabTool',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,    # 保留控制台，方便看服务地址与日志，关闭窗口即退出程序
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
