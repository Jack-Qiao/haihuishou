# -*- coding: utf-8 -*-
"""竞价侠自动抢单：查询列表 → 前端过滤 → 拉验机报告匹配条件 → 详情=抢单 + 出价。

参考嗨回收 grab_tool.py + app_ui._execute_task_* 三段式实现。"""

import re
import unicodedata
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

from .api import BiddingHeroAPI


# 竞价侠成色 9 档 + 保底价
GRADE_NAMES = ("全新", "靓机", "小花", "大花", "外爆", "内爆", "功能异常", "维修更换", "无法开机")
GRADE_KEYS = tuple("q_" + n for n in GRADE_NAMES)
GRADE_NAME_TO_KEY = dict(zip(GRADE_NAMES, GRADE_KEYS))
CONDITION_PRICE_KEYS = GRADE_KEYS + ("floorPrice",)


def _normalize_storage(s: Any) -> str:
    """把 16G+256G / 16+256G / 16GB+256GB → 16g+256g；供 conditions.storage 与订单存储值匹配。"""
    if s is None:
        return ""
    text = unicodedata.normalize("NFKC", str(s)).strip().lower()
    text = text.replace(" ", "")
    text = text.rstrip("|/\\,;，、")
    text = text.replace("gb", "g").replace("tb", "t")
    parts = re.findall(r"(\d+)\s*([gt])?", text)
    if not parts:
        return text
    return "+".join(num + (unit if unit else "g") for num, unit in parts)


def _pick(order: Dict[str, Any], keys: List[str], default: str = "") -> str:
    for k in keys:
        v = order.get(k)
        if v is not None and str(v).strip() != "":
            return str(v).strip()
    return default


def extract_storage_from_report(report: Dict[str, Any]) -> str:
    """从验机报告 report_data.inspection_items 中拼出存储字符串。
    优先 key_name == '内存'（形如 '8+128G'）；否则用 '系统内存' + '储存空间' 拼。"""
    if not isinstance(report, dict):
        return ""
    rd = report.get("report_data") or {}
    items = rd.get("inspection_items") or []
    if not isinstance(items, list):
        return ""
    ram = ""
    rom = ""
    combined = ""
    for it in items:
        if not isinstance(it, dict):
            continue
        kn = str(it.get("key_name") or "").strip()
        vn = str(it.get("value_name") or "").strip()
        if not kn or not vn:
            continue
        if kn == "内存":
            combined = vn
        elif kn == "系统内存":
            ram = vn
        elif kn == "储存空间":
            rom = vn
    if combined:
        return combined
    if ram and rom:
        return ram + "+" + rom
    return ram or rom or ""


@dataclass
class GrabCondition:
    category_names: List[str] = field(default_factory=list)   # cate_name 过滤（例："手机"）
    brand_names: List[str] = field(default_factory=list)      # brand_name 过滤
    channel_names: List[str] = field(default_factory=list)    # order_channel_name 过滤（前端叫「厂商」）
    min_price: Optional[str] = None
    max_price: Optional[str] = None
    max_amount: Optional[float] = None                        # 最大金额上限，超过不出价
    conditions: List[Dict[str, Any]] = field(default_factory=list)


def _match_price_range(order: Dict[str, Any], min_price: Optional[str], max_price: Optional[str]) -> bool:
    if not min_price and not max_price:
        return True
    for k in ("bid_amount", "reference_price", "start_price", "estimated_price"):
        v = order.get(k)
        if v is None or v == "":
            continue
        try:
            n = float(v)
        except (TypeError, ValueError):
            continue
        if min_price:
            try:
                if n < float(min_price):
                    return False
            except ValueError:
                pass
        if max_price:
            try:
                if n > float(max_price):
                    return False
            except ValueError:
                pass
        return True
    return True


def _norm_filter(s: str) -> str:
    """归一化过滤值：字母统一小写，去掉中文特殊符号/空格。"""
    import re as _re
    s = s.strip().lower()
    # 去掉中文/英文标点、空格、括号等
    s = _re.sub(r'[\s　 \(\)（）\[\]【】\{\}·\-—_/\\,，、:：;；!！?？.。··]+', '', s)
    return s


# API 返回的 brand_name → UI chip 品牌分类 的别名映射
_BRAND_ALIASES = {
    "苹果": "Apple",
    "华为智选": "华为",
    "其他品牌": "其他",
}


def _canonical_brand(name: str) -> str:
    """将 API 返回的 brand_name 映射到 UI chip 品牌分类。"""
    n = name.strip()
    mapped = _BRAND_ALIASES.get(n)
    if mapped:
        return mapped
    # 大小写不敏感匹配别名
    nl = n.lower()
    for k, v in _BRAND_ALIASES.items():
        if k.lower() == nl:
            return v
    return n


def filter_auction_list(orders: List[Dict[str, Any]], cond: GrabCondition) -> List[Dict[str, Any]]:
    """按品类/品牌/货源/价格区间对 auction_list 做前端过滤。"""
    cate_set = {_norm_filter(c) for c in (cond.category_names or []) if c}
    brand_set = {_norm_filter(b) for b in (cond.brand_names or []) if b}
    channel_set = {_norm_filter(c) for c in (cond.channel_names or []) if c}
    out = []
    for o in orders or []:
        if not isinstance(o, dict):
            continue
        if cate_set:
            v = _norm_filter(_pick(o, ["cate_name", "categoryName", "category"]))
            if v not in cate_set:
                continue
        if brand_set:
            raw = _pick(o, ["brand_name", "brandName", "brand"])
            canon = _canonical_brand(raw)
            v = _norm_filter(canon)
            if v not in brand_set:
                continue
        if channel_set:
            v = _norm_filter(_pick(o, ["order_channel_name", "channelName", "channel"]))
            if v not in channel_set:
                continue
        if not _match_price_range(o, cond.min_price, cond.max_price):
            continue
        out.append(o)
    return out


def _quote_from_condition(order: Dict[str, Any], cond_row: Dict[str, Any]) -> str:
    """按订单成色取报价：有成色时取对应列价（空则不出价）；空成色时用 floorPrice。"""
    grade_name = _pick(order, ["machine_level_name", "quality", "color_grade", "colorGrade", "grade"])
    if grade_name:
        key = GRADE_NAME_TO_KEY.get(grade_name.strip())
        if key:
            v = cond_row.get(key)
            if v is not None and str(v).strip():
                return str(v).strip()
            return ""  # 有成色但对应列价为空 → 不出价
    v = cond_row.get("floorPrice")
    if v is not None and str(v).strip():
        return str(v).strip()
    return ""


def _find_condition_for_order(
    order: Dict[str, Any],
    storage_norm: str,
    conditions: List[Dict[str, Any]],
) -> Optional[Dict[str, Any]]:
    order_model = _pick(order, ["model_name", "modelName", "productName", "name"]).lower()
    if not order_model:
        return None
    exact = None
    model_only = None
    for c in conditions or []:
        cm = str(c.get("modelName") or "").strip().lower()
        cs = _normalize_storage(c.get("storage"))
        if cm != order_model:
            continue
        if cs:
            if cs == storage_norm:
                exact = c
                break
        else:
            if model_only is None:
                model_only = c
    return exact or model_only


def match_and_price(
    api: BiddingHeroAPI,
    orders: List[Dict[str, Any]],
    conditions: List[Dict[str, Any]],
    max_amount: Optional[float],
) -> Tuple[List[Tuple[Dict[str, Any], str]], List[str]]:
    """per candidate 拉验机报告 → 匹配条件 → 得到 (order, bid_amount) 列表。"""
    matched: List[Tuple[Dict[str, Any], str]] = []
    errors: List[str] = []
    for o in orders:
        oid = _pick(o, ["id", "orderId", "order_id"])
        if not oid:
            continue
        report = api.get_order_report_safe(oid)
        storage_norm = _normalize_storage(extract_storage_from_report(report))
        row = _find_condition_for_order(o, storage_norm, conditions)
        if not row:
            continue
        price = _quote_from_condition(o, row)
        if not price:
            continue
        try:
            if max_amount is not None and float(price) > float(max_amount):
                continue
        except (TypeError, ValueError):
            errors.append("orderId=%s 价格格式异常: %s" % (oid, price))
            continue
        matched.append((o, price))
    return matched, errors


def grab_and_bid(
    api: BiddingHeroAPI,
    matched: List[Tuple[Dict[str, Any], str]],
) -> Tuple[int, int, List[str]]:
    """竞价侠：详情=抢单 → 出价。"""
    grabbed = 0
    quoted = 0
    errors: List[str] = []
    for o, bid_amount in matched:
        oid = _pick(o, ["id", "orderId", "order_id"])
        if not oid:
            continue
        try:
            api.get_order_detail(oid)
            grabbed += 1
        except Exception as e:
            errors.append("orderId=%s 抢单(详情)失败: %s" % (oid, str(e)))
            continue
        try:
            api.place_bid(order_id=oid, bid_amount=bid_amount)
            quoted += 1
        except Exception as e:
            errors.append("orderId=%s 出价失败: %s" % (oid, str(e)))
    return grabbed, quoted, errors


def normalize_conditions(raw: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], Optional[str]]:
    """归一化条件行：机型必填、(机型+存储) 不可重复；返回 (list, error_msg)。"""
    seen: Dict[str, int] = {}
    out: List[Dict[str, Any]] = []
    for idx, c in enumerate(raw or []):
        if not isinstance(c, dict):
            continue
        m = str(c.get("modelName") or "").strip()
        s = str(c.get("storage") or "").strip() or None
        if not m:
            continue
        key = m.lower() + "\x01" + ((s or "").lower())
        if key in seen:
            return [], "序号 %d 与 序号 %d 机型+存储不可重复" % (seen[key] + 1, idx + 1)
        seen[key] = idx
        row: Dict[str, Any] = {"modelName": m, "storage": s}
        for k in CONDITION_PRICE_KEYS:
            row[k] = str(c.get(k) or "").strip()
        out.append(row)
    if not out:
        return [], "请至少添加一条条件（机型必填，价格可空）"
    return out, None


def execute_task(
    api: BiddingHeroAPI,
    cond: GrabCondition,
    page_size: int = 3000,
) -> Dict[str, Any]:
    """整轮流程：拉全量列表 → 过滤 → 匹配 → 抢单出价。"""
    listing = api.get_auction_list(page_index=1, page_size=page_size)
    orders = listing.get("results") if isinstance(listing, dict) else None
    if not isinstance(orders, list):
        orders = []
    candidates = filter_auction_list(orders, cond)
    matched, match_errs = match_and_price(api, candidates, cond.conditions, cond.max_amount)
    grabbed, quoted, exec_errs = grab_and_bid(api, matched)
    return {
        "total": len(orders),
        "candidates": len(candidates),
        "matched": len(matched),
        "grabbed": grabbed,
        "quoted": quoted,
        "errors": (match_errs + exec_errs)[:30],
    }
