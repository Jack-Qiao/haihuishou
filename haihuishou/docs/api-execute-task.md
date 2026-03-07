# `/api/execute-task` 接口逐行说明

**作用**：执行一条「自动抢单」定时任务：按任务条件拉取待报价订单列表，匹配机型/存储/成色后抢单并提交报价。

**方法**：`POST`  
**请求体**：JSON，包含 `taskName`、`manufacturerNames`、`categoryId`、`brandIds`、`minPrice`、`maxPrice`、`conditions` 等。

---

## 一、路由与入参解析

| 行号 | 代码 | 说明 |
|------|------|------|
| 432-436 | `@app.route(...)`、`def api_execute_task():`、文档字符串 | 注册 POST 路由；文档说明 body 里可传任务名、厂商、分类、品牌、价格区间、条件列表。 |
| 437 | `data = request.get_json() or {}` | 读取请求体 JSON，没有则用空字典。 |
| 438-439 | `token = ...`、`user_id = ...` | 从请求头或 session 取 token；从 body 或 session 取 userId。 |
| 440-443 | `if not token:`、`if not user_id:`、`return ... 401` | 未登录：缺 token 或 userId 时直接返回 401。 |
| 444 | `task_name = (data.get("taskName") or "").strip()` | 取任务名称，用于错误提示里的「任务「xxx」：...」。 |
| 446-447 | `def task_err(msg):`、`return jsonify(...), 400` | 定义辅助函数：返回 400，且若有 task_name 则错误信息前缀「任务「名称」：msg」。 |
| 449-455 | `manufacturer_names`、`category_id`、`brand_ids`、`min_price`、`max_price` | 从 body 取厂商列表、分类 ID、品牌 ID 列表、最低价、最高价；厂商/品牌为字符串时按逗号拆成列表。 |
| 457 | `conditions = data.get("conditions") or []` | 取抢单条件数组。 |
| 458-464 | `if not conditions and (data.get("quoteAmount") or ...)` | **兼容旧格式**：若没有 conditions 但有 quoteAmount/modelName，则构造一条旧版条件 `{ quoteAmount, modelName, storage }`。 |
| 465-466 | `use_conditions_list = False`、`if conditions and ... "保底价" in conditions[0]` | 判断是否使用「新格式」：第一条条件是否包含「保底价」键。 |

---

## 二、新格式条件解析（保底价 + 成色价）

| 行号 | 代码 | 说明 |
|------|------|------|
| 467-468 | `use_conditions_list = True`、`normalized = []`、`seen_key = {}` | 进入新格式分支；准备归一化列表和「机型+存储」去重表。 |
| 469 | `for idx, c in enumerate(conditions):` | 遍历每条条件。 |
| 470-471 | `if not isinstance(c, dict): continue` | 非字典则跳过。 |
| 473-474 | `m = ...`、`s = ...`、`baodijia = ...` | 取机型、存储、保底价字符串。 |
| 475-476 | `if not m or not baodijia: continue` | 机型或保底价为空则跳过该条（不加入 normalized）。 |
| 478-483 | `try: bn = float(baodijia)`、范围 1～500、`return task_err(...)` | 保底价须为数字且在 1～500，否则返回带任务名的 400。 |
| 484-488 | `key = (m or "").lower() + "\x01" + (s or "").lower()`、`if key in seen_key`、`return task_err("序号 X 与 序号 Y 机型+存储不可重复")` | 用「机型小写 + 分隔符 + 存储小写」做唯一键；重复则报错并指出两条序号。 |
| 489 | `seen_key[key] = idx + 1` | 记录该 key 首次出现的序号（1-based）。 |
| 490 | `row = {"modelName": m, "storage": s or None}` | 当前条件先只含机型、存储。 |
| 491-509 | `for k in ("靓机", "小花", "大花", "外爆", "内爆", "保底价"):`、`v = str(c.get(k) or "").strip()`、`if v:`、范围校验、`row[k] = v`、`normalized.append(row)` | 对每个成色/保底价：转字符串、非空则校验 1～500 并写入 row；最后把 row 加入 normalized。 |
| 510-513 | `if not normalized:`、`return task_err(...)`、`conditions = normalized` | 若没有有效条件则报错；否则用 normalized 覆盖 conditions，供后面匹配用。 |

---

## 三、旧格式条件解析（仅报价金额 + 机型 + 存储）

| 行号 | 代码 | 说明 |
|------|------|------|
| 514-523 | `elif conditions:`、遍历 c、取 `quoteAmount`/`modelName`/`storage`、报价 1～500 校验、`normalized.append({"quoteAmount", "modelName", "storage"})` | 旧格式：每条条件只有报价金额、机型、存储；校验金额范围后加入 normalized。 |
| 524-525 | `if not normalized:`、`return task_err(...)`、`conditions = normalized` | 无有效条件则报错；否则 conditions 替换为归一化后的列表。 |
| 526-527 | `else:`、`return task_err("请添加至少一条抢单条件")` | 既没有新格式也没有旧格式条件时直接 400。 |

---

## 四、构造抢单查询条件并拉取订单列表

| 行号 | 代码 | 说明 |
|------|------|------|
| 528-529 | `remark = task_name or "定时任务"` | 报价备注用任务名或默认「定时任务」。 |
| 529 | `category_brands = [{"key": category_id, "value": brand_ids}] if category_id else []` | 组装分类+品牌，供下游接口查询。 |
| 530-536 | `cond = GrabCondition(...)` | 构造抢单条件：分类品牌、order_state="10"（待报价）、价格区间、厂商列表、每页 200。 |
| 537-539 | `api = HaihuishouAPI()`、`api.set_token(token, user_id)`、`tool = GrabOrderTool(api=api)` | 创建 API 客户端和抢单工具，注入 token 与 userId。 |
| 540 | `result = tool.step4_order_list(cond, page_index=1, user_id=user_id)` | **调用下游接口**拉取待报价订单列表（第一页）。 |
| 541-564 | 从 `result` 里多种可能结构取 `orderList` / `list` / `results` 等，最终得到 `lst`；`if not isinstance(lst, list): lst = []` | 兼容不同返回结构，统一得到订单数组 `lst`，保证为 list。 |

---

## 五、新格式：按机型+存储+成色匹配并算报价

| 行号 | 代码 | 说明 |
|------|------|------|
| 565 | `if use_conditions_list:` | 使用新格式条件（含保底价/成色价）时进入此分支。 |
| 566 | `def find_condition_and_quote(order):` | 定义：给定一条订单，找到匹配的条件并算出报价金额。 |
| 567-571 | `order_model = ...`、`order_storage = _normalize_storage(...)` | 取订单机型（小写）、存储（统一格式：去空格、小写）。 |
| 573-611 | `def quote_from_cond(cond):` | **成色取价**：先看订单 `colorGradeName` 有无值。 |
| 574-581 | `raw_name = order.get("colorGradeName")`；若为 None 或空字符串 | **无成色名**：直接返回该条件的「保底价」。 |
| 582-586 | `color_name = _normalize_color_name(raw_name)`；若规范化后仍空 | 再次确保无成色时走保底价。 |
| 587-595 | `CONDITION_GRADE_KEYS = ("靓机", "小花", "大花", "外爆", "内爆")`；先按「规范化后相等」匹配 key；再 `color_name in cond` | **有成色名**：先按已知成色 key 精确匹配（含 Unicode 规范化），再按原始 key 精确匹配，取到则返回该成色价。 |
| 600-610 | 对 key 做「key 与 color_name 互相包含」的模糊匹配；最后 `cond.get("保底价")` | 模糊匹配成色（如「大花（严重）」）；都不中则用保底价。 |
| 612-626 | `exact_match = None`、`model_only_match = None`；遍历 `conditions`；`c_m`/`c_s` 与 `order_model`/`order_storage` 比较 | **条件匹配**：优先「机型+存储」都相同的 exact_match；若无存储则只比机型，记入 model_only_match。 |
| 624-626 | `chosen = exact_match or model_only_match`；无则 `return None`；有则 `return quote_from_cond(chosen)` | 选中一条条件后，用该条件按上面成色逻辑算出报价并返回。 |
| 628-634 | `matched = []`；遍历 `lst`；取 `record_id`/`order_id`；`quote_for_submit = find_condition_and_quote(o)`；有报价则 `matched.append((o, quote_for_submit))` | 对每条订单调用上述函数；能算出报价的放入 `matched`（订单 + 报价金额）。 |

---

## 六、旧格式：仅按机型+存储匹配，报价用 quoteAmount

| 行号 | 代码 | 说明 |
|------|------|------|
| 636-653 | `else:`、`find_matching_condition(order_model, order_storage)`、按机型相等且（无存储或存储相等）找 cond；`matched.append((o, cond["quoteAmount"]))` | 旧格式：只按机型+存储匹配一条条件，报价直接用该条件的 `quoteAmount`。 |

---

## 七、抢单与报价提交

| 行号 | 代码 | 说明 |
|------|------|------|
| 666-667 | `grabbed = 0`、`quoted = 0`、`errors = []` | 统计抢单成功数、报价成功数，收集错误信息。 |
| 668-669 | `for item in matched:`、`o, quote_for_submit = item[0], item[1]` | 只对「已匹配并算出报价」的订单执行抢单+报价。 |
| 670-671 | 再次取 `record_id`、`order_id` | 从订单对象取接口所需 ID。 |
| 672 | `raw = api.grab_order(...)` | **调用抢单接口**。 |
| 673-679 | `sub_code = resp_data.get("subCode")`；200 记错误「抢单失败」；非 100 记「抢单异常」；100 则 `grabbed += 1` | 按 subCode 判断：200 多为已被抢，非 100 为异常，仅 100 视为抢单成功。 |
| 683-689 | `api.submit_quotation(record_id, order_id, actual_price=quote_for_submit, remark=remark, user_id=user_id)`、`quoted += 1` | 抢单成功后**提交报价**，金额为前面算出的 `quote_for_submit`，并累加报价成功数。 |
| 691-692 | `except Exception as e:`、`errors.append(...)` | 单条抢单/报价异常只记入 errors，不中断整批。 |
| 693-696 | `return jsonify({"success": True, "data": {"grabbed", "quoted", "total", "errors": errors[:20]}})` | 返回成功及抢单数、报价数、订单总数、最多 20 条错误。 |
| 697-698 | `except Exception as e:`、`return jsonify({"success": False, "message": str(e)}), 200` | 最外层异常（如拉列表失败）返回 200 但 success=False，message 为异常信息。 |

---

## 八、流程小结

1. **鉴权**：校验 token、userId，缺一则 401。  
2. **任务名**：取出 taskName，用于 task_err 前缀。  
3. **条件解析**：  
   - 新格式（含「保底价」）：校验机型+保底价、机型+存储不重复、成色价 1～500，得到 `conditions`。  
   - 旧格式：只校验报价+机型，得到 `conditions`。  
4. **拉列表**：用 GrabCondition 调 `step4_order_list` 拿到待报价订单列表 `lst`。  
5. **匹配与报价**：  
   - 新格式：每条订单按机型+存储匹配条件，再按 `colorGradeName` 有无值决定成色报价或保底价。  
   - 旧格式：按机型+存储匹配条件，报价用该条件的 `quoteAmount`。  
6. **执行**：对匹配到的订单先抢单（subCode=100 才成功），再提交报价；统计 grabbed、quoted，收集 errors。  
7. **返回**：`success: true` 时带上 grabbed、quoted、total、errors；异常时 `success: false` + message。
