"""
微信小程序抓包 - mitmproxy 插件
运行方式: mitmdump -p 8080 -s capture_addon.py
将系统/微信代理设置为 127.0.0.1:8080 后打开小程序即可抓取请求。
"""
import json
from datetime import datetime
from pathlib import Path

# 抓取数据保存目录（与脚本同目录下的 wechat_capture 文件夹）
CAPTURE_DIR = Path(__file__).resolve().parent / "wechat_capture"
# 只保存这些域名的请求（空列表表示保存全部）
ALLOWED_HOSTS: list[str] = []
# 排除的域名（静态资源、统计等可排除）
EXCLUDED_HOSTS = [
    "wx.qlogo.cn",
    "mmbiz.qpic.cn",
    "res.wx.qq.com",
    "tracer.qcloud.com",
]


def _ensure_capture_dir():
    CAPTURE_DIR.mkdir(parents=True, exist_ok=True)


def _get_session_file():
    """按日期分文件，便于按天查看。"""
    _ensure_capture_dir()
    date_str = datetime.now().strftime("%Y%m%d")
    return CAPTURE_DIR / f"capture_{date_str}.jsonl"


def _should_capture(host: str) -> bool:
    if EXCLUDED_HOSTS and host in EXCLUDED_HOSTS:
        return False
    if not ALLOWED_HOSTS:
        return True
    return any(host == h or host.endswith("." + h) for h in ALLOWED_HOSTS)


def _safe_content(content: bytes | None, max_len: int = 1024 * 512) -> str | None:
    if content is None:
        return None
    if len(content) > max_len:
        return f"<truncated {len(content)} bytes>"
    try:
        return content.decode("utf-8", errors="replace")
    except Exception:
        return "<binary>"


def _record(flow):
    try:
        host = flow.request.pretty_host
        if not _should_capture(host):
            return

        req = flow.request
        res = flow.response
        if res is None:
            return

        entry = {
            "time": datetime.now().isoformat(),
            "method": req.method,
            "url": req.pretty_url,
            "host": host,
            "request_headers": dict(req.headers),
            "request_content": _safe_content(req.raw_content),
            "status_code": res.status_code,
            "response_headers": dict(res.headers),
            "response_content": _safe_content(res.raw_content),
        }
        path = _get_session_file()
        with open(path, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    except Exception as e:
        # 避免插件报错导致 mitmproxy 退出
        with open(CAPTURE_DIR / "error.log", "a", encoding="utf-8") as f:
            f.write(f"{datetime.now().isoformat()} {e}\n")


def response(flow):
    """mitmproxy 钩子：收到响应时写入一条记录。"""
    _record(flow)
