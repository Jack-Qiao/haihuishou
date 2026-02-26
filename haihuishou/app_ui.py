# -*- coding: utf-8 -*-
"""
嗨回收抢单工具 - Web UI 服务端。
启动后浏览器访问 http://127.0.0.1:5050
"""

import os
import sys
from typing import Any, Dict

from flask import Flask, jsonify, render_template, request, session

from .api import HaihuishouAPI
from .grab_tool import GrabCondition, GrabOrderTool

# 打包成 exe 时模板在 sys._MEIPASS 下
_base_dir = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
_template_dir = os.path.join(_base_dir, "templates")
app = Flask(__name__, template_folder=_template_dir)
app.secret_key = os.environ.get("HAIHUISHOU_SECRET_KEY", "haihuishou-grab-dev-secret")
app.config["JSON_AS_ASCII"] = False


def _api_with_session() -> HaihuishouAPI:
    api = HaihuishouAPI()
    token = session.get("token")
    uid = session.get("user_id") or session.get("userId")
    if token:
        api.set_token(token, uid)
    return api


def _tool_with_session() -> GrabOrderTool:
    return GrabOrderTool(api=_api_with_session())


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/login", methods=["POST"])
def api_login():
    data = request.get_json() or {}
    login_name = (data.get("loginName") or "").strip()
    login_pwd = data.get("loginPwd") or ""
    if not login_name or not login_pwd:
        return jsonify({"success": False, "message": "请填写手机号和密码"}), 400
    try:
        tool = _tool_with_session()
        info = tool.step1_login(login_name, login_pwd)
        session["token"] = info.get("token")
        uid = info.get("userId") or info.get("user_id")
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
    """获取当前登录用户信息（姓名、手机、余额等）。"""
    api = _api_with_session()
    if not api.token or not api.user_id:
        return jsonify({"success": False, "message": "未登录"}), 401
    try:
        data = api.query_user_info()
        return jsonify({"success": True, "data": data})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 200


@app.route("/api/categories", methods=["GET"])
def api_categories():
    try:
        tool = _tool_with_session()
        data = tool.step2_manufacturer_and_categories()
        return jsonify({"success": True, "data": data})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 200


@app.route("/api/brands", methods=["GET"])
def api_brands():
    cat_id = request.args.get("catId", type=int)
    if cat_id is None:
        return jsonify({"success": False, "message": "缺少 catId"}), 400
    try:
        tool = _tool_with_session()
        brands = tool.step3_brands_by_category(cat_id)
        return jsonify({"success": True, "data": brands})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 200


@app.route("/api/order-list", methods=["POST"])
def api_order_list():
    body = request.get_json() or {}
    # 优先用请求里的 token（headers）和 userId（body），没有则用 session
    token = request.headers.get("token") or session.get("token")
    user_id = body.get("userId") or session.get("user_id") or session.get("userId")
    if not token:
        return jsonify({"success": False, "message": "请先登录（缺少 token，需放在请求头）"}), 401
    if not user_id:
        return jsonify({"success": False, "message": "请先登录（缺少 userId，需放在请求体）"}), 401
    # categoryBrands: 电子产品+品牌 [{"key": "100001", "value": ["100007", "100011"]}]
    category_brands = body.get("categoryBrands") or []
    order_state = (body.get("orderState") or "10").strip()
    min_price = (body.get("minPrice") or "").strip() or None
    max_price = (body.get("maxPrice") or "").strip() or None
    sub_order_source_names = body.get("subOrderSourceNames") or []  # 厂商名称列表
    if isinstance(sub_order_source_names, str):
        sub_order_source_names = [x.strip() for x in sub_order_source_names.split(",") if x.strip()]
    page = int(body.get("pageIndex", 1))
    page_size = int(body.get("pageSize", 20))
    cond = GrabCondition(
        category_brands=category_brands,
        order_state=order_state,
        min_price=min_price,
        max_price=max_price,
        sub_order_source_names=sub_order_source_names,
        page_size=page_size,
    )
    try:
        api = HaihuishouAPI()
        api.set_token(token, user_id)
        tool = GrabOrderTool(api=api)
        result = tool.step4_order_list(cond, page_index=page, user_id=user_id)
        # 出参：data.pageCount 为列表总数，data.result.orderList 为订单列表
        if isinstance(result, list):
            result = {"results": result, "totalCount": len(result)}
        elif isinstance(result, dict):
            lst = None
            res_obj = result.get("result")
            if isinstance(res_obj, dict):
                lst = res_obj.get("orderList")
            if lst is None:
                lst = (
                    result.get("list")
                    or result.get("orderList")
                    or result.get("results")
                    or result.get("records")
                    or result.get("rows")
                    or result.get("items")
                )
            if lst is None and isinstance(result.get("data"), list):
                lst = result["data"]
            if lst is None and isinstance(result.get("data"), dict):
                inner = result["data"]
                lst = inner.get("result", {}).get("orderList") if isinstance(inner.get("result"), dict) else None
                lst = lst or inner.get("list") or inner.get("orderList") or inner.get("results") or []
            if not isinstance(lst, list):
                lst = []
            total = result.get("pageCount") or result.get("totalCount")
            if total is None:
                total = len(lst)
            result = {"results": lst, "totalCount": total}
        return jsonify({"success": True, "data": result})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 200


@app.route("/api/grab-order", methods=["POST"])
def api_grab_order():
    """先抢单，成功后再允许报价。body: recordId, orderId, userId；header: token。"""
    data = request.get_json() or {}
    token = request.headers.get("token") or session.get("token")
    user_id = data.get("userId") or session.get("user_id") or session.get("userId")
    if not token:
        return jsonify({"success": False, "message": "请先登录（缺少 token）"}), 401
    if not user_id:
        return jsonify({"success": False, "message": "请先登录（缺少 userId）"}), 401
    record_id = data.get("recordId")
    order_id = data.get("orderId")
    if record_id is None or record_id == "" or order_id is None or order_id == "":
        return jsonify({"success": False, "message": "缺少 recordId 或 orderId"}), 400
    try:
        api = HaihuishouAPI()
        api.set_token(token, user_id)
        raw = api.grab_order(record_id=record_id, order_id=order_id, user_id=user_id)
        resp_data = raw.get("data") or {}
        sub_code = resp_data.get("subCode")
        sub_message = (resp_data.get("subMessage") or "").strip()
        # 出参成功 subCode=100（抢单成功），失败 subCode=200（如已被其他报价师抢单）
        if sub_code == 200:
            return jsonify({"success": False, "message": sub_message or "抢单失败"}), 200
        if sub_code == 100:
            return jsonify({"success": True, "data": resp_data})
        return jsonify({"success": True, "data": resp_data})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 200


@app.route("/api/quote", methods=["POST"])
def api_quote():
    data = request.get_json() or {}
    token = request.headers.get("token") or session.get("token")
    user_id = data.get("userId") or session.get("user_id") or session.get("userId")
    if not token:
        return jsonify({"success": False, "message": "请先登录（缺少 token）"}), 401
    if not user_id:
        return jsonify({"success": False, "message": "请先登录（缺少 userId）"}), 401
    record_id = data.get("recordId")
    order_id = data.get("orderId")
    actual_price = data.get("actualPrice")  # 手动填写
    remark = (data.get("remark") or "").strip()  # 手动填写
    if record_id is None or order_id is None or actual_price is None or actual_price == "":
        return jsonify({"success": False, "message": "缺少 recordId / orderId / actualPrice（报价金额必填）"}), 400
    try:
        api = HaihuishouAPI()
        api.set_token(token, user_id)
        tool = GrabOrderTool(api=api)
        res = tool.step5_submit_quotation(
            record_id=int(record_id),
            order_id=int(order_id),
            actual_price=str(actual_price),
            quote_result=int(data.get("quoteResult", 1)),
            remark=remark,
            user_id=user_id,
        )
        return jsonify({"success": True, "data": res})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 200


@app.route("/api/update-quote", methods=["POST"])
def api_update_quote():
    """已报价列表的修改报价，调用 hsdupdatequotation。body: recordId, orderId, actualPrice, remark, userId。"""
    data = request.get_json() or {}
    token = request.headers.get("token") or session.get("token")
    user_id = data.get("userId") or session.get("user_id") or session.get("userId")
    if not token:
        return jsonify({"success": False, "message": "请先登录（缺少 token）"}), 401
    if not user_id:
        return jsonify({"success": False, "message": "请先登录（缺少 userId）"}), 401
    record_id = data.get("recordId")
    order_id = data.get("orderId")
    actual_price = data.get("actualPrice")
    remark = (data.get("remark") or "").strip()
    if record_id is None or order_id is None or actual_price is None or actual_price == "":
        return jsonify({"success": False, "message": "缺少 recordId / orderId / actualPrice（报价金额必填）"}), 400
    try:
        api = HaihuishouAPI()
        api.set_token(token, user_id)
        res = api.update_quotation(
            record_id=record_id,
            order_id=order_id,
            actual_price=str(actual_price),
            remark=remark,
            user_id=user_id,
        )
        return jsonify({"success": True, "data": res})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 200


def main():
    host = os.environ.get("HAIHUISHOU_UI_HOST", "127.0.0.1")
    port = int(os.environ.get("HAIHUISHOU_UI_PORT", "5050"))
    debug = not getattr(sys, "frozen", False)
    if not debug:
        import webbrowser
        import threading
        def _open_browser():
            import time
            time.sleep(1.2)
            webbrowser.open(f"http://{host}:{port}")
        threading.Thread(target=_open_browser, daemon=True).start()
    app.run(host=host, port=port, debug=debug)


if __name__ == "__main__":
    main()
