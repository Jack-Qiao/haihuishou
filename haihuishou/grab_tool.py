# -*- coding: utf-8 -*-
"""
抢单工具：登录 → 获取分类/品牌 → 设置抢单条件 → 查询订单列表 → 报价提交。
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from .api import HaihuishouAPI, md5_password


@dataclass
class GrabCondition:
    """抢单条件设置（gethsdorderlist 入参，无省份城市）。"""

    # 电子产品类型+品牌，格式 [{"key": "100001", "value": ["100007", "100011"]}]
    category_brands: List[Dict[str, Any]] = field(default_factory=list)
    # 订单状态，默认 "10" 表示未被下单的
    order_state: str = "10"
    # 价格区间，None 表示不传该字段
    min_price: Optional[str] = None
    max_price: Optional[str] = None
    # 厂商名称列表（如 华为、OPPO、小米、荣耀），用于 subOrderSourceNames
    sub_order_source_names: List[str] = field(default_factory=list)
    # 每页条数
    page_size: int = 20


class GrabOrderTool:
    """抢单流程封装。"""

    def __init__(self, api: Optional[HaihuishouAPI] = None):
        self.api = api or HaihuishouAPI()

    def step1_login(self, login_name: str, login_pwd: str, **kwargs: Any) -> Dict[str, Any]:
        """1. 登录，拿到用户信息与 token。"""
        info = self.api.login(login_name, login_pwd, **kwargs)
        return info

    def step2_manufacturer_and_categories(self) -> Dict[str, Any]:
        """2. 获取厂商列表、电子产品类型。"""
        manufacturer_list = self.api.get_manufacturer_list()
        cat_list = self.api.get_sys_category()
        return {
            "manufacturerList": manufacturer_list,
            "catList": cat_list,
        }

    def step3_brands_by_category(self, cat_id: int) -> List[Dict[str, str]]:
        """3. 根据电子产品类型查询品牌。"""
        return self.api.get_sys_brand(cat_id)

    def step4_order_list(
        self,
        condition: GrabCondition,
        page_index: int = 1,
        user_id: Optional[str] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """4. 按抢单条件查询订单列表（gethsdorderlist，需 headers 的 token + body 的 userId）。"""
        if not self.api.token:
            raise RuntimeError("请先登录，列表查询需要 token（请求头）")
        uid = user_id or self.api.user_id
        if not uid:
            raise RuntimeError("请先登录，列表查询需要 userId（请求体）")
        return self.api.get_hsd_order_list(
            page_index=page_index,
            page_size=condition.page_size,
            order_state=condition.order_state,
            category_brands=condition.category_brands or None,
            min_price=condition.min_price,
            max_price=condition.max_price,
            sub_order_source_names=condition.sub_order_source_names or None,
            user_id=uid,
        )

    def step5_submit_quotation(
        self,
        record_id: int,
        order_id: int,
        actual_price: str,
        quote_result: int = 1,
        remark: str = "",
        user_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """5. 报价提交（需要 token + userId，请求体带 userId）。"""
        if not self.api.token:
            raise RuntimeError("请先登录，报价需要 token")
        uid = user_id or self.api.user_id
        if not uid:
            raise RuntimeError("请先登录，报价需要 userId")
        return self.api.submit_quotation(
            record_id=record_id,
            order_id=order_id,
            actual_price=actual_price,
            quote_result=quote_result,
            remark=remark,
            user_id=uid,
        )

    def run_full_flow(
        self,
        login_name: str,
        login_pwd: str,
        condition: GrabCondition,
        page_index: int = 1,
        submit_quotes: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """
        执行完整流程：登录 → 分类/品牌 → 按条件查列表。
        submit_quotes 若提供，格式为 [{"record_id": int, "order_id": int, "actual_price": str, "remark": ""}, ...]
        """
        result: Dict[str, Any] = {"login": None, "categories": None, "order_list": None, "quotes": []}
        result["login"] = self.step1_login(login_name, login_pwd)
        result["categories"] = self.step2_manufacturer_and_categories()
        result["order_list"] = self.step4_order_list(condition, page_index=page_index)
        if submit_quotes:
            for item in submit_quotes:
                quote_res = self.step5_submit_quotation(
                    record_id=item["record_id"],
                    order_id=item["order_id"],
                    actual_price=item["actual_price"],
                    quote_result=item.get("quote_result", 1),
                    remark=item.get("remark", ""),
                )
                result["quotes"].append({"request": item, "response": quote_res})
        return result
