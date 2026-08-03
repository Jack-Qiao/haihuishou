# -*- coding: utf-8 -*-
"""
启动竞价侠 Web UI。
在 biddingHero 项目目录执行：python -m biddinghero.run_ui
或：python biddinghero/run_ui.py
默认地址：http://127.0.0.1:5070
"""

import sys
import os

def _main():
    _here = os.path.dirname(os.path.abspath(__file__))
    _project = os.path.dirname(_here)
    if _project not in sys.path:
        sys.path.insert(0, _project)
    from biddinghero.app_ui import main
    main()

if __name__ == "__main__":
    _main()
