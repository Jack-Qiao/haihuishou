#!/usr/bin/env python3
"""
读取抓包结果（JSONL），按 URL/域名汇总或导出为 JSON/CSV。
用法:
  python export_data.py                    # 列出最近抓取的文件
  python export_data.py wechat_capture/capture_20250223.jsonl  # 解析指定文件
  python export_data.py --json out.json    # 导出为单个 JSON
  python export_data.py --by-host          # 按 host 分组统计
"""
import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

CAPTURE_DIR = Path(__file__).resolve().parent / "wechat_capture"


def load_jsonl(path: Path):
    """逐行读取 JSONL，yield 每条记录。"""
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                yield json.loads(line)
            except json.JSONDecodeError:
                continue


def list_captures():
    """列出所有抓取文件。"""
    if not CAPTURE_DIR.exists():
        print("尚未有抓取数据，请先运行 run_capture.py 并访问小程序。")
        return
    files = sorted(CAPTURE_DIR.glob("capture_*.jsonl"), key=lambda p: p.stat().st_mtime, reverse=True)
    if not files:
        print("wechat_capture/ 下暂无 capture_*.jsonl 文件。")
        return
    print("抓取文件（按时间倒序）:")
    for f in files[:20]:
        size = f.stat().st_size
        print(f"  {f.name}  ({size} bytes)")


def summarize(path: Path, by_host: bool = False):
    """统计或按 host 分组。"""
    host_count = defaultdict(int)
    url_count = defaultdict(int)
    total = 0
    for rec in load_jsonl(path):
        total += 1
        host_count[rec.get("host", "")] += 1
        url_count[rec.get("url", "")] += 1
    print(f"总请求数: {total}")
    if by_host:
        print("\n按 host:")
        for h, c in sorted(host_count.items(), key=lambda x: -x[1]):
            print(f"  {h}: {c}")
    print("\n请求次数最多的 URL (前 10):")
    for url, c in sorted(url_count.items(), key=lambda x: -x[1])[:10]:
        print(f"  {c}  {url[:80]}..." if len(url) > 80 else f"  {c}  {url}")


def export_json(path: Path, out_path: Path):
    """导出为单个 JSON 数组。"""
    records = list(load_jsonl(path))
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False, indent=2)
    print(f"已导出 {len(records)} 条到 {out_path}")


def main():
    parser = argparse.ArgumentParser(description="解析/导出微信小程序抓包数据")
    parser.add_argument("file", nargs="?", type=Path, help="capture_*.jsonl 文件路径")
    parser.add_argument("--json", type=Path, help="导出为 JSON 文件")
    parser.add_argument("--by-host", action="store_true", help="按 host 分组统计")
    args = parser.parse_args()

    if not args.file:
        list_captures()
        return

    if not args.file.is_absolute():
        args.file = (Path.cwd() / args.file).resolve()
    if not args.file.exists():
        print(f"文件不存在: {args.file}", file=sys.stderr)
        sys.exit(1)

    if args.json:
        export_json(args.file, args.json)
    else:
        summarize(args.file, by_host=args.by_host)


if __name__ == "__main__":
    main()
