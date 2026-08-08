# -*- coding: utf-8 -*-
"""竞价侠 API 封装：登录、列表、详情、报价等。

接口基地址：https://jingjiaxia.com
除登录外均使用 Authorization: Bearer <token>。
"""

import json
import os
import requests
from typing import Any, Dict, List, Optional

requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)


def _ssl_verify() -> bool:
    v = os.environ.get("BIDDINGHERO_SSL_VERIFY", "0").strip().lower()
    return v in ("1", "true", "yes")


BIDDING_API = "https://jingjiaxia.com"


class BiddingHeroAPI:
    """竞价侠 API 客户端，支持登录与 Bearer token 鉴权。"""

    def __init__(
        self,
        base_url: str = BIDDING_API,
        timeout: int = 15,
        verify: Optional[bool] = None,
    ):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.verify = verify if verify is not None else _ssl_verify()
        self._token: Optional[str] = None
        self._user_id: Optional[str] = None

    def _headers(self, with_token: bool = False) -> Dict[str, str]:
        h = {
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        }
        if with_token and self._token:
            h["Authorization"] = "Bearer " + self._token
        return h

    def set_token(self, token: str, user_id: Optional[str] = None) -> None:
        self._token = token
        if user_id is not None:
            self._user_id = str(user_id)

    @property
    def token(self) -> Optional[str]:
        return self._token

    @property
    def user_id(self) -> Optional[str]:
        return self._user_id

    # ------------------------- 1. 登录 -------------------------

    def login(self, phone: str, password: str) -> Dict[str, Any]:
        url = self.base_url + "/api/base/login/"
        payload = {"phone": phone, "password": password}
        r = requests.post(url, json=payload, headers=self._headers(with_token=False),
                          timeout=self.timeout, verify=self.verify)
        r.raise_for_status()
        data = r.json()
        if data.get("code") is not None and data.get("code") != 0:
            raise RuntimeError(data.get("msg", "登录失败"))
        info = data.get("data", {}) or {}
        token = info.get("token")
        user = info.get("user") or {}
        uid = user.get("id")
        if token:
            self._token = token
        if uid is not None:
            self._user_id = str(uid)
        return info

    def get_my_info(self) -> Dict[str, Any]:
        if not self._token:
            raise ValueError("获取用户信息需要 token，请先登录")
        url = self.base_url + "/api/base/users/getMyInfo/"
        r = requests.get(url, headers=self._headers(with_token=True),
                         timeout=self.timeout, verify=self.verify)
        r.raise_for_status()
        data = r.json() if r.text.strip() else {}
        if data.get("code") is not None and data.get("code") != 0:
            raise RuntimeError(data.get("msg", "获取用户信息失败"))
        return data.get("data", {}) or {}

    # ------------------------- 2. 列表接口 -------------------------

    def get_auction_list(self, page_index: int = 1, page_size: int = 3000) -> Dict[str, Any]:
        """查询列表（可竞价商品）。"""
        if not self._token:
            raise ValueError("查询列表需要 token，请先登录")
        url = self.base_url + "/api/base/orders/auction_list/"
        params = {"pageIndex": page_index, "pageSize": page_size}
        r = requests.get(url, params=params, headers=self._headers(with_token=True),
                         timeout=self.timeout, verify=self.verify)
        r.raise_for_status()
        try:
            data = r.json() if r.text.strip() else {}
        except (ValueError, json.JSONDecodeError):
            raise RuntimeError("列表接口返回非 JSON，请确认已登录且 token 有效")
        if data.get("code") is not None and data.get("code") != 0:
            raise RuntimeError(data.get("msg", "查询列表失败"))
        return data.get("data", {}) or {}

    def get_grab_order_list(self) -> List[Dict[str, Any]]:
        """报价中列表（当前用户已查看详情、正在报价的商品）。"""
        if not self._token:
            raise ValueError("查询报价中列表需要 token，请先登录")
        url = self.base_url + "/api/base/orders/grab_order_list/"
        r = requests.get(url, headers=self._headers(with_token=True),
                         timeout=self.timeout, verify=self.verify)
        r.raise_for_status()
        try:
            data = r.json() if r.text.strip() else {}
        except (ValueError, json.JSONDecodeError):
            raise RuntimeError("报价中列表接口返回非 JSON")
        raw = data.get("data")
        if isinstance(raw, list):
            return raw
        if data.get("code") is not None and data.get("code") != 0:
            # 允许「暂无抢单数据」这种空态
            if raw is None:
                return []
            raise RuntimeError(data.get("msg", "查询报价中列表失败"))
        return raw or []

    def get_my_bids(
        self,
        page_index: int = 1,
        page_size: int = 20,
        status: str = "bidding",
        created_at_after: Optional[str] = None,
        created_at_before: Optional[str] = None,
    ) -> Dict[str, Any]:
        """已报价列表。"""
        if not self._token:
            raise ValueError("查询已报价列表需要 token，请先登录")
        url = self.base_url + "/api/base/bid-records/my_bids/"
        params: Dict[str, Any] = {
            "pageIndex": page_index,
            "pageSize": page_size,
            "status": status,
        }
        if created_at_after:
            params["created_at_after"] = created_at_after
        if created_at_before:
            params["created_at_before"] = created_at_before
        r = requests.get(url, params=params, headers=self._headers(with_token=True),
                         timeout=self.timeout, verify=self.verify)
        r.raise_for_status()
        try:
            data = r.json() if r.text.strip() else {}
        except (ValueError, json.JSONDecodeError):
            raise RuntimeError("已报价列表接口返回非 JSON")
        if data.get("code") is not None and data.get("code") != 0:
            raise RuntimeError(data.get("msg", "查询已报价列表失败"))
        return data.get("data", {}) or {}

    # ------------------------- 3. 详情接口 -------------------------

    def get_order_detail(self, order_id: Any) -> Dict[str, Any]:
        """商品详情。查看详情后，服务端会将此商品加入到「报价中列表」（grab_order_list）。"""
        if not self._token:
            raise ValueError("获取详情需要 token，请先登录")
        url = self.base_url + "/api/base/orders/" + str(order_id) + "/detail_info/"
        r = requests.get(url, headers=self._headers(with_token=True),
                         timeout=self.timeout, verify=self.verify)
        r.raise_for_status()
        try:
            data = r.json() if r.text.strip() else {}
        except (ValueError, json.JSONDecodeError):
            raise RuntimeError("详情接口返回非 JSON")
        if data.get("code") is not None and data.get("code") != 0:
            raise RuntimeError(data.get("msg", "获取详情失败"))
        return data.get("data", data) or {}

    # ------------------------- 4. 操作接口 -------------------------

    def place_bid(self, order_id: Any, bid_amount: Any) -> Dict[str, Any]:
        """出价接口（竞价侠可直接出价，无需先抢单）。"""
        if not self._token:
            raise ValueError("出价需要 token，请先登录")
        url = self.base_url + "/api/base/orders/" + str(order_id) + "/place_bid/"
        payload = {"bid_amount": str(bid_amount)}
        r = requests.post(url, json=payload, headers=self._headers(with_token=True),
                          timeout=self.timeout, verify=self.verify)
        r.raise_for_status()
        try:
            data = r.json() if r.text.strip() else {}
        except (ValueError, json.JSONDecodeError):
            raise RuntimeError("出价接口返回非 JSON")
        if data.get("code") is not None and data.get("code") != 0:
            raise RuntimeError(data.get("msg", "出价失败"))
        return data.get("data", data) or {}

    def get_reference_price(self, order_number: Any) -> Dict[str, Any]:
        """根据订单编号查询市场价格参考。

        通过订单号（order_number，形如 P202608081819354366）获取该机的市场参考价与成色价位。
        """
        if not self._token:
            raise ValueError("查询参考价需要 token，请先登录")
        url = self.base_url + "/api/base/products/reference-price-by-order/"
        r = requests.get(url, params={"order_number": str(order_number)},
                         headers=self._headers(with_token=True),
                         timeout=self.timeout, verify=self.verify)
        r.raise_for_status()
        try:
            data = r.json() if r.text.strip() else {}
        except (ValueError, json.JSONDecodeError):
            raise RuntimeError("参考价接口返回非 JSON")
        if data.get("code") is not None and data.get("code") != 0:
            raise RuntimeError(data.get("msg", "查询参考价失败"))
        return data.get("data", data) or {}

    def cancel_grab_order(self, order_id: Any) -> Dict[str, Any]:
        """取消抢单。"""
        if not self._token:
            raise ValueError("取消抢单需要 token，请先登录")
        url = self.base_url + "/api/base/orders/" + str(order_id) + "/cancel_grab_order/"
        r = requests.post(url, json={}, headers=self._headers(with_token=True),
                          timeout=self.timeout, verify=self.verify)
        r.raise_for_status()
        try:
            data = r.json() if r.text.strip() else {}
        except (ValueError, json.JSONDecodeError):
            raise RuntimeError("取消抢单接口返回非 JSON")
        if data.get("code") is not None and data.get("code") != 0:
            raise RuntimeError(data.get("msg", "取消抢单失败"))
        return data.get("data", data) or {}
