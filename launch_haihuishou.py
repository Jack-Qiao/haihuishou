# -*- coding: utf-8 -*-
"""
嗨回收抢单工具 - 打包后的入口。
直接运行此脚本会启动 Web 服务并打开浏览器。
在项目根目录（codingAi）执行打包：pyinstaller haihuishou.spec
"""

import sys
import os

# 打包后当前目录可能在 bundle 内，需把项目根加入 path 以便 import haihuishou
if getattr(sys, "frozen", False):
    _root = sys._MEIPASS
else:
    _root = os.path.dirname(os.path.abspath(__file__))
if _root not in sys.path:
    sys.path.insert(0, _root)

from haihuishou.app_ui import main

if __name__ == "__main__":
    main()
