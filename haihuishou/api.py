# -*- coding: utf-8 -*-
"""
嗨回收 API 封装：登录、分类、品牌、订单列表、报价等。
列表查询和报价需要在请求头中携带 token。
"""

import hashlib
import json
import os
import requests
from typing import Any, Dict, List, Optional

# 关闭 SSL 校验时不再打印 InsecureRequestWarning
requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)


def _ssl_verify() -> bool:
    """对方接口证书链含自签名时需关闭校验；设为 1/true 可恢复校验。"""
    v = os.environ.get("HAIHUISHOU_SSL_VERIFY", "0").strip().lower()
    return v in ("1", "true", "yes")

# 基础域名
HSD_API = "https://hsdapi.haihuishou.com"
HAIHUISHOU_API = "https://haihuishou.com"
WAP_API = "https://wap.haihuishou.com"


def md5_password(password: str) -> str:
    """将明文密码转为接口要求的 MD5 字符串（32 位小写）。"""
    return hashlib.md5(password.encode("utf-8")).hexdigest()


class HaihuishouAPI:
    """嗨回收 API 客户端，支持登录与 token 鉴权。"""

    def __init__(
        self,
        base_hsd: str = HSD_API,
        base_main: str = HAIHUISHOU_API,
        base_wap: str = WAP_API,
        timeout: int = 15,
        verify: Optional[bool] = None,
    ):
        self.base_hsd = base_hsd.rstrip("/")
        self.base_main = base_main.rstrip("/")
        self.base_wap = base_wap.rstrip("/")
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
            h["token"] = self._token
        return h

    def set_token(self, token: str, user_id: Optional[str] = None) -> None:
        self._token = token
        if user_id is not None:
            self._user_id = user_id

    @property
    def token(self) -> Optional[str]:
        return self._token

    @property
    def user_id(self) -> Optional[str]:
        return self._user_id

    # ------------------------- 1. 登录 -------------------------

    def login(
        self,
        login_name: str,
        login_pwd: str,
        client: str = "001001002",
        login_type: int = 1,
        device_name: str = "",
    ) -> Dict[str, Any]:
        """
        登录获取 token 和用户信息。
        login_pwd 可为明文（内部会做 MD5）或已是 32 位小写 MD5 字符串。
        """
        pwd = login_pwd if len(login_pwd) == 32 and all(c in "0123456789abcdef" for c in login_pwd) else md5_password(login_pwd)
        url = f"{self.base_hsd}/api/login/checklogin"
        payload = {
            "client": client,
            "deviceName": device_name,
            "loginName": login_name,
            "loginPwd": pwd,
            "loginType": login_type,
        }
        r = requests.post(
            url, json=payload, headers=self._headers(with_token=False), timeout=self.timeout, verify=self.verify
        )
        r.raise_for_status()
        data = r.json()
        if data.get("code") != 1 or not data.get("success"):
            raise RuntimeError(data.get("message", "登录失败"))
        info = data.get("data", {})
        self._token = info.get("token")
        self._user_id = info.get("userId")
        return info

    def query_user_info(self, user_id: Optional[str] = None) -> Dict[str, Any]:
        """
        获取用户信息（queryuserinfo）。
        需要 token，body 传 userId。
        """
        uid = user_id or self._user_id
        if not uid:
            raise ValueError("查询用户信息需要 userId，请先登录")
        if not self._token:
            raise ValueError("查询用户信息需要 token，请先登录")
        url = f"{self.base_hsd}/api/user/queryuserinfo"
        r = requests.post(
            url,
            json={"userId": uid},
            headers=self._headers(with_token=True),
            timeout=self.timeout,
            verify=self.verify,
        )
        r.raise_for_status()
        data = r.json()
        if data.get("code") != 1 or not data.get("success"):
            raise RuntimeError(data.get("message", "获取用户信息失败"))
        return data.get("data", {})

    # ------------------------- 2. 厂商与分类 -------------------------

    def get_manufacturer_list(self) -> List[Dict[str, str]]:
        """获取厂商列表。"""
        url = f"{self.base_hsd}/api/syscategory/getmanufacturerdata"
        r = requests.post(
            url, json={}, headers=self._headers(with_token=False), timeout=self.timeout, verify=self.verify
        )
        r.raise_for_status()
        data = r.json()
        if data.get("code") != 1:
            raise RuntimeError(data.get("message", "获取厂商列表失败"))
        return data.get("data", {}).get("manufacturerList", [])

    def get_sys_category(self) -> List[Dict[str, Any]]:
        """获取电子产品类型（如手机、平板、笔记本）。"""
        url = f"{self.base_hsd}/api/syscategory/getsyscategory"
        r = requests.post(
            url, json={}, headers=self._headers(with_token=False), timeout=self.timeout, verify=self.verify
        )
        r.raise_for_status()
        data = r.json()
        if data.get("code") != 1:
            raise RuntimeError(data.get("message", "获取分类失败"))
        return data.get("data", {}).get("catList", [])

    def get_sys_brand(self, cat_id: int) -> List[Dict[str, str]]:
        """根据电子产品类型（catId）查询该类型下的品牌。"""
        url = f"{self.base_hsd}/api/syscategory/getsysbrand"
        r = requests.post(
            url,
            json={"catId": cat_id},
            headers=self._headers(with_token=False),
            timeout=self.timeout,
            verify=self.verify,
        )
        r.raise_for_status()
        data = r.json()
        if data.get("code") != 1:
            raise RuntimeError(data.get("message", "获取品牌列表失败"))
        return data.get("data", {}).get("brandList", [])

    # ------------------------- 4. 抢单列表（需要 token） -------------------------

    def get_hsd_order_list(
        self,
        page_index: int = 1,
        page_size: int = 100,
        order_state: str = "10",
        category_brands: Optional[List[Dict[str, Any]]] = None,
        min_price: Optional[str] = None,
        max_price: Optional[str] = None,
        sub_order_source_names: Optional[List[str]] = None,
        user_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        查询订单列表（gethsdorderlist）。
        入参必须：body 里带 userId，headers 里带 token。
        categoryBrands：电子产品类型+品牌 [{"key": "分类id", "value": ["品牌id"]}]
        subOrderSourceNames：厂商名称列表（如 华为、OPPO、小米、荣耀）
        orderState：默认 "10" 表示未被下单的。
        """
        uid = user_id or self._user_id
        if not uid:
            raise ValueError("查询订单列表需要 userId，请先登录")
        if not self._token:
            raise ValueError("查询订单列表需要 token（请求头），请先登录")
        url = f"{self.base_hsd}/api/orderquery/gethsdorderlist"
        payload = {
            "pageIndex": page_index,
            "pageSize": page_size,
            "orderState": order_state,
            "categoryBrands": category_brands or [],
            "subOrderSourceNames": sub_order_source_names or [],
            "userId": uid,
        }
        if min_price is not None:
            payload["minPrice"] = min_price
        if max_price is not None:
            payload["maxPrice"] = max_price
        headers = self._headers(with_token=True)
        r = requests.post(
            url,
            json=payload,
            headers=headers,
            timeout=self.timeout,
            verify=self.verify,
        )
        r.raise_for_status()
        try:
            data = r.json() if r.text.strip() else {}
        except (ValueError, json.JSONDecodeError):
            raise RuntimeError("订单列表接口返回非 JSON，请确认已登录且 token 有效")
        if data.get("code") is not None and data.get("code") != 1:
            raise RuntimeError(data.get("message", "查询订单列表失败"))
        inner = data.get("data", data)
        if isinstance(inner, dict) and "list" not in inner:
            for key in ("list", "results", "records", "orderList"):
                if key in data and data[key] is not None:
                    inner = {**inner, "list": data[key]}
                    break
        return inner

    def grab_order_query(self, **body: Any) -> Dict[str, Any]:
        """抢单查询接口（wap 域），需要 token。"""
        url = f"{self.base_wap}/api/miniProgram/hd/order/grabOrderQuery"
        r = requests.post(
            url,
            json=body or {},
            headers=self._headers(with_token=True),
            timeout=self.timeout,
            verify=self.verify,
        )
        r.raise_for_status()
        return r.json()

    # ------------------------- 4.5 抢单（需要 token，成功后再报价） -------------------------

    def grab_order(
        self,
        record_id: Any,
        order_id: Any,
        user_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """抢单，成功后才能报价。body: recordId(int), orderId(int), userId(str)。出参成功 subCode=100，失败 subCode=200。"""
        uid = user_id or self._user_id
        if not uid:
            raise ValueError("抢单需要 userId，请先登录或传入 user_id")
        if not self._token:
            raise ValueError("抢单需要 token，请先登录")
        url = f"{self.base_hsd}/api/orderoper/hsdgraborder"
        payload = {
            "recordId": int(record_id),
            "orderId": int(order_id),
            "userId": uid,
        }
        r = requests.post(
            url,
            json=payload,
            headers=self._headers(with_token=True),
            timeout=self.timeout,
            verify=self.verify,
        )
        r.raise_for_status()
        return r.json() if r.text.strip() else {}

    # ------------------------- 5. 报价提交（需要 token） -------------------------

    def submit_quotation(
        self,
        record_id: int,
        order_id: int,
        actual_price: str,
        quote_result: int = 1,
        remark: str = "",
        user_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """提交报价，需要 token。"""
        url = f"{self.base_hsd}/api/orderoper/hsdquotation"
        uid = user_id or self._user_id
        if not uid:
            raise ValueError("报价需要 userId，请先登录或传入 user_id")
        payload = {
            "recordId": record_id,
            "orderId": order_id,
            "quoteResult": quote_result,
            "actualPrice": str(actual_price),
            "remark": remark,
            "userId": uid,
        }
        r = requests.post(
            url,
            json=payload,
            headers=self._headers(with_token=True),
            timeout=self.timeout,
            verify=self.verify,
        )
        r.raise_for_status()
        data = r.json()
        if data.get("code") != 1:
            raise RuntimeError(data.get("message", data.get("data", {}).get("subMessage", "报价失败")))
        return data.get("data", {})

    def update_quotation(
        self,
        record_id: Any,
        order_id: Any,
        actual_price: str,
        remark: str = "",
        user_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """修改报价（已报价订单），POST hsdupdatequotation。入参 actualPrice, remark, orderId, recordId, userId。成功 subCode=100。"""
        uid = user_id or self._user_id
        if not uid:
            raise ValueError("修改报价需要 userId，请先登录或传入 user_id")
        if not self._token:
            raise ValueError("修改报价需要 token，请先登录")
        url = f"{self.base_hsd}/api/orderoper/hsdupdatequotation"
        payload = {
            "actualPrice": str(actual_price),
            "remark": remark,
            "orderId": int(order_id),
            "recordId": int(record_id),
            "userId": uid,
        }
        r = requests.post(
            url,
            json=payload,
            headers=self._headers(with_token=True),
            timeout=self.timeout,
            verify=self.verify,
        )
        r.raise_for_status()
        data = r.json() if r.text.strip() else {}
        resp_data = data.get("data") or {}
        if data.get("code") != 1 or resp_data.get("subCode") != 100:
            raise RuntimeError(resp_data.get("subMessage", data.get("message", "修改报价失败")))
        return resp_data
