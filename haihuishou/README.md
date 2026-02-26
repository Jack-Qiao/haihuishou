# 嗨回收抢单工具

基于嗨回收微信小程序接口的抢单工具，流程：**登录 → 获取分类/品牌 → 设置抢单条件 → 查询订单列表 → 报价提交**。  
列表查询与报价需在请求头中携带 **token**（登录后自动维护）。

## 流程说明

1. **登录**：调用 `POST /api/login/checklogin`，获取 `token`、`userId` 等，后续列表与报价请求自动带 token。
2. **获取基础数据**：厂商列表 `getmanufacturerdata`、电子产品类型 `getsyscategory`（如手机、平板、笔记本）。
3. **按类型查品牌**：`getsysbrand` 传入 `catId`，得到该类型下的品牌列表（用于筛选订单）。
4. **抢单条件查询**：`getTheOrderList` 支持按品牌、省市、可锁单状态等条件分页查询订单列表。
5. **报价提交**：`hsdquotation` 传入 `recordId`、`orderId`、`actualPrice`、`userId` 等提交报价。

## 环境

- Python 3.8+
- 依赖：`pip install -r requirements.txt`

## 打包成可执行程序（其他电脑免安装 Python 直接运行）

在**项目根目录**（即 `codingAi`，与 `haihuishou` 同级）执行：

```bash
# 1. 安装打包依赖
pip install pyinstaller

# 2. 执行打包（会生成 dist/haihuishou_app 或单文件 exe，视平台而定）
pyinstaller haihuishou.spec
```

- **Windows**：打包后在 `dist` 目录得到 `haihuishou_app.exe`，双击运行即可；会弹出控制台窗口显示服务地址，浏览器会自动打开 http://127.0.0.1:5050 ，关闭控制台窗口即退出程序。
- **macOS / Linux**：得到 `dist/haihuishou_app` 可执行文件，在终端执行 `./haihuishou_app` 即可。

将 `dist` 里生成的**可执行文件**（或整个 `dist/haihuishou_app` 文件夹，若为目录形式）复制到其他电脑，无需安装 Python 即可直接运行使用。

**在 Windows 上打包：** PyInstaller 只能在本机系统打包，要得到 `haihuishou_app.exe` 需在 **Windows 电脑**上执行上述命令（在项目根目录先 `pip install pyinstaller`，再 `pyinstaller haihuishou.spec`）。若没有 Windows 环境，可把代码推到 GitHub，在仓库 **Actions** 里运行 **Build Windows** 工作流（支持手动触发），完成后在 Artifacts 中下载 `haihuishou-windows` 即可得到 `haihuishou_app.exe`。

## 使用方式

### 1. 安装依赖

```bash
cd haihuishou
pip install -r requirements.txt
```

### 2. 启动 Web UI（推荐）

在浏览器中操作：登录、获取分类/品牌、设置抢单条件、查询订单列表、提交报价。

```bash
# 在项目根目录（codingAi）下执行
python3 -m haihuishou.run_ui
```

或在 `haihuishou` 目录下执行：

```bash
cd haihuishou
python3 run_ui.py
```

启动后浏览器访问 **http://127.0.0.1:5050**。  
可选环境变量：`HAIHUISHOU_UI_HOST`、`HAIHUISHOU_UI_PORT`（默认 5050）；`HAIHUISHOU_SECRET_KEY`（Session 密钥，生产环境请设置）。

### 3. 环境变量（可选）

- `HAIHUISHOU_LOGIN_NAME`：登录手机号  
- `HAIHUISHOU_LOGIN_PWD`：登录密码（明文即可，程序会做 MD5）
- `HAIHUISHOU_SSL_VERIFY`：请求对方 API 时是否校验 HTTPS 证书，默认不校验（`0`），避免自签名证书导致登录失败；设为 `1` 可恢复校验。

不设置则执行需登录的子命令时会提示输入。

### 4. 命令行子命令

在项目根目录（codingAi）下以模块方式运行（若使用 Python 3 可把 `python` 改为 `python3`）：

```bash
# 在 codingAi 根目录
python -m haihuishou.main login
python -m haihuishou.main categories
python -m haihuishou.main brands 100001
python -m haihuishou.main list --brand-ids 100010,100007 --province 320000 --city 320100 --page 1
python -m haihuishou.main quote <record_id> <order_id> <actual_price> --remark "备注"
```

- **login**：登录并打印用户信息（含 token）。
- **categories**：获取厂商列表与电子产品类型（无需登录）。
- **brands**：根据分类 id 获取品牌，如 `100001` 表示手机（无需登录）。
- **list**：按条件查询可抢订单列表（**需要先登录**）；可传 `--brand-ids`、`--province`、`--city`、`--page`、`--page-size`。
- **quote**：提交报价（**需要先登录**）；`record_id`、`order_id` 来自订单列表或详情接口返回，`actual_price` 为报价金额。

### 5. 在代码中调用

```python
from haihuishou import HaihuishouAPI, GrabOrderTool, GrabCondition

api = HaihuishouAPI()
tool = GrabOrderTool(api=api)

# 1. 登录
tool.step1_login("你的手机号", "你的密码")

# 2. 厂商与分类
data = tool.step2_manufacturer_and_categories()
# data["manufacturerList"], data["catList"]

# 3. 某分类下的品牌（如手机 100001）
brands = tool.step3_brands_by_category(100001)

# 4. 抢单条件与列表
cond = GrabCondition(
    brand_ids=["100010", "100007"],  # 品牌 id
    province_code="320000",
    city_code="320100",
    page_size=100,
)
orders = tool.step4_order_list(cond, page_index=1)
# orders["results"] 为订单列表，orders["totalCount"] 为总数

# 5. 报价（record_id、order_id 需从订单/明细接口获取）
tool.step5_submit_quotation(
    record_id=357663322,
    order_id=7456252,
    actual_price="1",
    remark="123",
)
```

订单列表中的每条订单可能包含 `orderNo`、`orderProductList` 等；提交报价所需的 `recordId`、`orderId` 若列表接口未直接返回，需从订单详情或相关接口中获取，请以实际接口字段为准。

## 目录结构

```
haihuishou/
├── README.md         # 说明
├── requirements.txt
├── api.py            # 接口封装（登录、分类、品牌、订单列表、报价）
├── grab_tool.py      # 抢单流程与条件设置
├── main.py           # CLI 入口
├── app_ui.py         # Web UI 服务端（Flask）
├── run_ui.py         # 启动 Web UI
├── templates/
│   └── index.html    # 抢单工具单页界面（登录 + 抢单 + 定时任务 Tab）
└── __init__.py
```

## 注意

- 仅用于学习或经授权的调试，请遵守平台规则与相关法律法规。
- 请勿将账号密码提交到仓库；建议使用环境变量或本地配置。
