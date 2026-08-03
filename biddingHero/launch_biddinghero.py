# -*- coding: utf-8 -*-
"""
竞价侠 - 快捷启动。
用法: python launch_biddinghero.py [选项]
  -p 端口  默认 5070
  -H 地址  默认 127.0.0.1（对外用 0.0.0.0）
  -d       调试模式（不自动打开浏览器）
打包: 在本目录执行 pyinstaller biddinghero.spec
"""

import argparse
import os
import sys

if getattr(sys, "frozen", False):
    _root = sys._MEIPASS
else:
    _root = os.path.dirname(os.path.abspath(__file__))
if _root not in sys.path:
    sys.path.insert(0, _root)

from biddinghero.app_ui import app


def main():
    parser = argparse.ArgumentParser(description="竞价侠")
    parser.add_argument("-p", "--port", type=int, default=5070, help="端口 (默认 5070)")
    parser.add_argument("-H", "--host", default="127.0.0.1", metavar="HOST", help="监听地址 (默认 127.0.0.1)")
    parser.add_argument("-d", "--debug", action="store_true", help="调试模式")
    args = parser.parse_args()

    os.environ["BIDDINGHERO_UI_HOST"] = args.host
    os.environ["BIDDINGHERO_UI_PORT"] = str(args.port)
    if args.debug:
        os.environ["BIDDINGHERO_DEBUG"] = "1"

    if not args.debug:
        import threading
        import webbrowser

        def _open():
            import time
            time.sleep(1.2)
            url_host = "127.0.0.1" if args.host == "0.0.0.0" else args.host
            webbrowser.open("http://{}:{}".format(url_host, args.port))

        threading.Thread(target=_open, daemon=True).start()

    app.run(host=args.host, port=args.port, debug=args.debug)


if __name__ == "__main__":
    main()
