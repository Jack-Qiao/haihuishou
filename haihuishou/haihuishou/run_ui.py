# -*- coding: utf-8 -*-
"""
启动抢单工具 Web UI。
在 haihuishou 项目目录执行：python -m haihuishou.run_ui
或：python haihuishou/run_ui.py
默认地址：http://127.0.0.1:5050
"""

import sys
import os

def _main():
    # 保证项目目录在 path 中，以便 import haihuishou
    _here = os.path.dirname(os.path.abspath(__file__))
    _project = os.path.dirname(_here)
    if _project not in sys.path:
        sys.path.insert(0, _project)
    from haihuishou.app_ui import main
    main()

if __name__ == "__main__":
    _main()
