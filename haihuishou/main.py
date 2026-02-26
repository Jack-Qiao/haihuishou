# -*- coding: utf-8 -*-
"""
抢单工具入口：支持交互式步骤或一次性执行。
使用前请设置环境变量 HAIHUISHOU_LOGIN_NAME、HAIHUISHOU_LOGIN_PWD（可选，否则会提示输入）。
"""

import argparse
import json
import os
import sys
from typing import Optional

from .api import HaihuishouAPI
from .grab_tool import GrabCondition, GrabOrderTool


def _env(name: str, default: str = "") -> str:
    return os.environ.get(name, default).strip()


def cmd_login(tool: GrabOrderTool, name: str, pwd: str) -> None:
    info = tool.step1_login(name, pwd)
    print("登录成功:")
    print(json.dumps(info, ensure_ascii=False, indent=2))


def cmd_categories(tool: GrabOrderTool) -> None:
    data = tool.step2_manufacturer_and_categories()
    print("厂商列表:", json.dumps(data["manufacturerList"], ensure_ascii=False, indent=2))
    print("电子产品类型:", json.dumps(data["catList"], ensure_ascii=False, indent=2))


def cmd_brands(tool: GrabOrderTool, cat_id: int) -> None:
    brands = tool.step3_brands_by_category(cat_id)
    print("品牌列表:", json.dumps(brands, ensure_ascii=False, indent=2))


def cmd_list(
    tool: GrabOrderTool,
    cat_id: str,
    brand_ids: str,
    order_state: str,
    min_price: str,
    max_price: str,
    page: int,
    page_size: int,
) -> None:
    bid_list = [x.strip() for x in (brand_ids or "").split(",") if x.strip()]
    category_brands = []
    if (cat_id or "").strip() and bid_list:
        category_brands = [{"key": cat_id.strip(), "value": bid_list}]
    cond = GrabCondition(
        category_brands=category_brands,
        order_state=order_state or "18",
        min_price=min_price or "1",
        max_price=max_price or "5609",
        page_size=page_size,
    )
    data = tool.step4_order_list(cond, page_index=page)
    results = data.get("results", [])
    total = data.get("totalCount", 0)
    print(f"订单列表 (共 {total} 条，本页 {len(results)} 条):")
    print(json.dumps(results, ensure_ascii=False, indent=2, default=str))


def cmd_quote(
    tool: GrabOrderTool,
    record_id: int,
    order_id: int,
    actual_price: str,
    remark: str,
) -> None:
    res = tool.step5_submit_quotation(
        record_id=record_id,
        order_id=order_id,
        actual_price=actual_price,
        remark=remark,
    )
    print("报价结果:", json.dumps(res, ensure_ascii=False, indent=2))


def main() -> int:
    parser = argparse.ArgumentParser(description="嗨回收抢单工具")
    parser.add_argument("--login-name", default=_env("HAIHUISHOU_LOGIN_NAME"), help="登录手机号")
    parser.add_argument("--login-pwd", default=_env("HAIHUISHOU_LOGIN_PWD"), help="登录密码（明文或 MD5）")
    sub = parser.add_subparsers(dest="command", help="子命令")

    sub.add_parser("login", help="登录并获取 token")
    p_cat = sub.add_parser("categories", help="获取厂商列表与电子产品类型")
    p_brands = sub.add_parser("brands", help="根据分类 id 获取品牌")
    p_brands.add_argument("cat_id", type=int, help="分类 id，如 100001=手机")
    p_list = sub.add_parser("list", help="按条件查询可抢订单列表（需先 login，无省份城市）")
    p_list.add_argument("--cat-id", default="", help="分类 id，如 100001=手机")
    p_list.add_argument("--brand-ids", default="", help="品牌 id 逗号分隔，如 100067,100611")
    p_list.add_argument("--order-state", default="10", help="订单状态，默认 10=未被下单的")
    p_list.add_argument("--min-price", default="1", help="最低价")
    p_list.add_argument("--max-price", default="5000", help="最高价")
    p_list.add_argument("--page", type=int, default=1, help="页码")
    p_list.add_argument("--page-size", type=int, default=100, help="每页条数")
    p_quote = sub.add_parser("quote", help="提交报价（需先 login）")
    p_quote.add_argument("record_id", type=int, help="记录 id")
    p_quote.add_argument("order_id", type=int, help="订单 id")
    p_quote.add_argument("actual_price", help="报价金额")
    p_quote.add_argument("--remark", default="", help="备注")

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        return 0

    need_login = args.command in ("list", "quote")
    login_name = args.login_name or ""
    login_pwd = args.login_pwd or ""

    if need_login and not (login_name and login_pwd):
        login_name = input("登录手机号: ").strip()
        login_pwd = input("登录密码: ").strip()
        if not (login_name and login_pwd):
            print("需要登录信息", file=sys.stderr)
            return 1

    api = HaihuishouAPI()
    tool = GrabOrderTool(api=api)

    if need_login:
        try:
            tool.step1_login(login_name, login_pwd)
        except Exception as e:
            print(f"登录失败: {e}", file=sys.stderr)
            return 1

    try:
        if args.command == "login":
            name = login_name or input("登录手机号: ").strip()
            pwd = login_pwd or input("登录密码: ").strip()
            if not (name and pwd):
                print("需要登录手机号和密码", file=sys.stderr)
                return 1
            cmd_login(tool, name, pwd)
        elif args.command == "categories":
            cmd_categories(tool)
        elif args.command == "brands":
            cmd_brands(tool, args.cat_id)
        elif args.command == "list":
            cmd_list(
                tool,
                getattr(args, "cat_id", "") or "",
                getattr(args, "brand_ids", "") or "",
                getattr(args, "order_state", "10") or "10",
                getattr(args, "min_price", "1") or "1",
                getattr(args, "max_price", "5000") or "5000",
                getattr(args, "page", 1),
                getattr(args, "page_size", 100),
            )
        elif args.command == "quote":
            cmd_quote(
                tool,
                args.record_id,
                args.order_id,
                args.actual_price,
                getattr(args, "remark", ""),
            )
    except Exception as e:
        print(f"执行失败: {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
