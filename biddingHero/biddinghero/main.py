# -*- coding: utf-8 -*-
"""竞价侠 CLI 入口。"""

import argparse
import json
import os
import sys

from .api import BiddingHeroAPI


def _env(name: str, default: str = "") -> str:
    return os.environ.get(name, default).strip()


def main() -> int:
    parser = argparse.ArgumentParser(description="竞价侠 CLI")
    parser.add_argument("--phone", default=_env("BIDDINGHERO_PHONE"), help="登录手机号")
    parser.add_argument("--password", default=_env("BIDDINGHERO_PASSWORD"), help="登录密码")
    sub = parser.add_subparsers(dest="command", help="子命令")

    sub.add_parser("login", help="登录并获取 token")
    p_list = sub.add_parser("list", help="查询列表")
    p_list.add_argument("--page", type=int, default=1)
    p_list.add_argument("--page-size", type=int, default=100)
    p_grab = sub.add_parser("grab-list", help="报价中列表")
    p_bids = sub.add_parser("my-bids", help="已报价列表")
    p_bids.add_argument("--page", type=int, default=1)
    p_bids.add_argument("--page-size", type=int, default=20)
    p_bids.add_argument("--status", default="bidding")
    p_detail = sub.add_parser("detail", help="商品详情")
    p_detail.add_argument("order_id")
    p_bid = sub.add_parser("bid", help="出价")
    p_bid.add_argument("order_id")
    p_bid.add_argument("bid_amount")
    p_cancel = sub.add_parser("cancel", help="取消抢单")
    p_cancel.add_argument("order_id")

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        return 0

    phone = args.phone or input("手机号: ").strip()
    pwd = args.password or input("密码: ").strip()
    if not phone or not pwd:
        print("需要手机号和密码", file=sys.stderr)
        return 1

    api = BiddingHeroAPI()
    try:
        api.login(phone, pwd)
    except Exception as e:
        print("登录失败: " + str(e), file=sys.stderr)
        return 1

    def _print(obj):
        print(json.dumps(obj, ensure_ascii=False, indent=2, default=str))

    try:
        if args.command == "login":
            print("登录成功，userId=" + str(api.user_id))
        elif args.command == "list":
            _print(api.get_auction_list(page_index=args.page, page_size=args.page_size))
        elif args.command == "grab-list":
            _print(api.get_grab_order_list())
        elif args.command == "my-bids":
            _print(api.get_my_bids(page_index=args.page, page_size=args.page_size, status=args.status))
        elif args.command == "detail":
            _print(api.get_order_detail(args.order_id))
        elif args.command == "bid":
            _print(api.place_bid(args.order_id, args.bid_amount))
        elif args.command == "cancel":
            _print(api.cancel_grab_order(args.order_id))
    except Exception as e:
        print("执行失败: " + str(e), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
