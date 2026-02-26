# -*- coding: utf-8 -*-
"""
启动抢单工具 Web UI。
在项目根目录执行：python -m haihuishou.run_ui
或在 haihuishou 目录执行：python run_ui.py
默认地址：http://127.0.0.1:5050
"""

import sys
import os

def _main():
    # 在 haihuishou 目录下执行时，把上级目录加入 path 以便 import haihuishou
    _here = os.path.dirname(os.path.abspath(__file__))
    _root = os.path.dirname(_here)
    if _root not in sys.path:
        sys.path.insert(0, _root)
    from haihuishou.app_ui import main
    main()

if __name__ == "__main__":
    _main()
