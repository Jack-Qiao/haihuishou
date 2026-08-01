#!/usr/bin/env python3
"""
启动微信小程序抓包代理（mitmdump + 插件）。
默认监听 8080，需在系统或微信中配置代理为 127.0.0.1:8080。
"""
import shutil
import subprocess
import sys
from pathlib import Path

ADDON = Path(__file__).resolve().parent / "capture_addon.py"
PORT = 8080


def main():
    # mitmproxy 安装后提供的是 mitmdump 命令，不是 python -m mitmdump
    mitmdump = shutil.which("mitmdump")
    if mitmdump:
        cmd = [mitmdump, "-p", str(PORT), "-s", str(ADDON), "--set", "block_global=false"]
    else:
        try:
            import mitmproxy  # noqa: F401
        except ImportError:
            print("未检测到 mitmproxy，请先安装依赖：")
            print("  pip3 install -r requirements.txt")
            sys.exit(1)
        # 若 PATH 里没有 mitmdump，用当前 Python 的 mitmproxy 模块
        cmd = [
            sys.executable,
            "-m",
            "mitmproxy.tools.mitmdump",
            "-p", str(PORT),
            "-s", str(ADDON),
            "--set", "block_global=false",
        ]
    print(f"启动抓包代理: http(s)://127.0.0.1:{PORT}")
    print("请将系统或微信代理设置为 127.0.0.1:" + str(PORT))
    print("抓取数据将保存到 wechat_capture/ 目录，按 Ctrl+C 停止。")
    subprocess.run(cmd)


if __name__ == "__main__":
    main()
