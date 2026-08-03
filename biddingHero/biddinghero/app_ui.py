# -*- coding: utf-8 -*-
"""
竞价侠 - Web UI 服务端。
启动后浏览器访问 http://127.0.0.1:5060
"""

import os
import sys
import threading
from typing import Any, Dict, List

from flask import Flask, jsonify, render_template, request, session

from .api import BiddingHeroAPI


_base_dir = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
_template_dir = os.path.join(_base_dir, "templates")
app = Flask(__name__, template_folder=_template_dir)
app.secret_key = os.environ.get("BIDDINGHERO_SECRET_KEY", "biddinghero-dev-secret")
app.config["JSON_AS_ASCII"] = False


def _api_with_session() -> BiddingHeroAPI:
    api = BiddingHeroAPI()
    token = session.get("token")
    uid = session.get("user_id") or session.get("userId")
    if token:
        api.set_token(token, uid)
    return api


def _extract_order_id(item: Any) -> Any:
    """从报价中列表 item 里取商品 id；item 可能就是 id 字符串或数字。"""
    if isinstance(item, dict):
        for key in ("orderId", "order_id", "id"):
            v = item.get(key)
            if v is not None:
                return v
        return None
    return item


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/login", methods=["POST"])
def api_login():
    data = request.get_json() or {}
    phone = (data.get("phone") or data.get("loginName") or "").strip()
    password = data.get("password") or data.get("loginPwd") or ""
    if not phone or not password:
        return jsonify({"success": False, "message": "请填写手机号和密码"}), 400
    try:
        api = BiddingHeroAPI()
        info = api.login(phone, password)
        session["token"] = api.token
        uid = api.user_id
        session["user_id"] = uid
        session["userId"] = uid
        return jsonify({"success": True, "data": info})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 200


@app.route("/api/logout", methods=["POST"])
def api_logout():
    session.pop("token", None)
    session.pop("user_id", None)
    session.pop("userId", None)
    return jsonify({"success": True})


@app.route("/api/status")
def api_status():
    token = session.get("token")
    uid = session.get("user_id") or session.get("userId")
    if token and uid:
        return jsonify({"loggedIn": True, "userId": uid, "token": token})
    return jsonify({"loggedIn": False, "userId": None})


@app.route("/api/user-info", methods=["GET"])
def api_user_info():
    """获取当前登录用户信息。"""
    api = _api_with_session()
    if not api.token:
        return jsonify({"success": False, "message": "未登录"}), 401
    try:
        data = api.get_my_info()
        return jsonify({"success": True, "data": data})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 200


@app.route("/api/order-list", methods=["GET", "POST"])
def api_order_list():
    """待竞价列表。"""
    body = request.get_json(silent=True) or {}
    api = _api_with_session()
    if not api.token:
        return jsonify({"success": False, "message": "请先登录"}), 401
    page_index = int(body.get("pageIndex") or request.args.get("pageIndex") or 1)
    page_size = int(body.get("pageSize") or request.args.get("pageSize") or 3000)
    try:
        data = api.get_auction_list(page_index=page_index, page_size=page_size)
        # 统一结构：results / totalCount
        results = data.get("results") if isinstance(data, dict) else None
        total = data.get("count") if isinstance(data, dict) else None
        if results is None and isinstance(data, list):
            results = data
        if results is None:
            results = []
        if total is None:
            total = len(results)
        return jsonify({"success": True, "data": {"results": results, "totalCount": total}})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 200


@app.route("/api/grab-order-list", methods=["GET"])
def api_grab_order_list():
    """报价中列表：查看详情后商品会进入这个列表。"""
    api = _api_with_session()
    if not api.token:
        return jsonify({"success": False, "message": "请先登录"}), 401
    try:
        lst = api.get_grab_order_list()
        # 提取纯 id 列表，供前端做对比
        ids: List[Any] = []
        for it in lst or []:
            oid = _extract_order_id(it)
            if oid is not None:
                ids.append(oid)
        return jsonify({"success": True, "data": {"results": lst or [], "ids": ids}})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 200


@app.route("/api/my-bids", methods=["GET"])
def api_my_bids():
    """已报价列表。"""
    api = _api_with_session()
    if not api.token:
        return jsonify({"success": False, "message": "请先登录"}), 401
    page_index = int(request.args.get("pageIndex", 1))
    page_size = int(request.args.get("pageSize", 20))
    status = (request.args.get("status") or "bidding").strip()
    created_at_after = (request.args.get("created_at_after") or "").strip() or None
    created_at_before = (request.args.get("created_at_before") or "").strip() or None
    try:
        data = api.get_my_bids(
            page_index=page_index,
            page_size=page_size,
            status=status,
            created_at_after=created_at_after,
            created_at_before=created_at_before,
        )
        results = data.get("results") if isinstance(data, dict) else None
        total = data.get("count") if isinstance(data, dict) else None
        if results is None:
            results = []
        if total is None:
            total = len(results)
        return jsonify({"success": True, "data": {"results": results, "totalCount": total}})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 200


@app.route("/api/order-detail", methods=["GET"])
def api_order_detail():
    """商品详情。看完详情后此商品即进入报价中列表。"""
    api = _api_with_session()
    if not api.token:
        return jsonify({"success": False, "message": "请先登录"}), 401
    order_id = request.args.get("orderId")
    if not order_id:
        return jsonify({"success": False, "message": "缺少 orderId"}), 400
    try:
        data = api.get_order_detail(order_id)
        # 再拉一次报价中列表，返回给前端做同步
        grab_ids: List[Any] = []
        try:
            grab_list = api.get_grab_order_list()
            for it in grab_list or []:
                oid = _extract_order_id(it)
                if oid is not None:
                    grab_ids.append(oid)
        except Exception:
            grab_list = []
        return jsonify({
            "success": True,
            "data": {
                "detail": data,
                "grabList": grab_list,
                "grabIds": grab_ids,
            },
        })
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 200


@app.route("/api/place-bid", methods=["POST"])
def api_place_bid():
    """出价接口。前端可直接从列表出价。"""
    data = request.get_json() or {}
    api = _api_with_session()
    if not api.token:
        return jsonify({"success": False, "message": "请先登录"}), 401
    order_id = data.get("orderId")
    bid_amount = data.get("bidAmount") or data.get("actualPrice")
    if not order_id or bid_amount in (None, ""):
        return jsonify({"success": False, "message": "缺少 orderId / bidAmount"}), 400
    try:
        res = api.place_bid(order_id=order_id, bid_amount=bid_amount)
        return jsonify({"success": True, "data": res})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 200


@app.route("/api/cancel-grab-order", methods=["POST"])
def api_cancel_grab_order():
    """取消抢单（把商品从报价中列表移除）。"""
    data = request.get_json() or {}
    api = _api_with_session()
    if not api.token:
        return jsonify({"success": False, "message": "请先登录"}), 401
    order_id = data.get("orderId")
    if not order_id:
        return jsonify({"success": False, "message": "缺少 orderId"}), 400
    try:
        res = api.cancel_grab_order(order_id=order_id)
        return jsonify({"success": True, "data": res})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 200


@app.route("/api/shutdown", methods=["POST"])
def api_shutdown():
    def _exit():
        import time
        time.sleep(1.5)
        os._exit(0)

    threading.Thread(target=_exit, daemon=False).start()
    return jsonify({"success": True, "message": "工具即将关闭"})


def main():
    host = os.environ.get("BIDDINGHERO_UI_HOST", "127.0.0.1")
    port = int(os.environ.get("BIDDINGHERO_UI_PORT", "5070"))
    debug = not getattr(sys, "frozen", False)
    if not debug:
        import webbrowser
        def _open_browser():
            import time
            time.sleep(1.2)
            webbrowser.open("http://{}:{}".format(host, port))
        threading.Thread(target=_open_browser, daemon=True).start()
    app.run(host=host, port=port, debug=debug)


if __name__ == "__main__":
    main()
