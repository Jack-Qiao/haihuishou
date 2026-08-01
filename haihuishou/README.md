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

## 使用方式

### 1. 安装依赖

```bash
cd haihuishou
pip install -r requirements.txt
```

### 2. 启动 Web UI（推荐）

```bash
cd haihuishou
./run
# 或
python3 launch_haihuishou.py
# 或
python3 -m haihuishou.run_ui
```

启动后浏览器访问 **http://127.0.0.1:5050**。  
可选参数：`-p` 端口、`-H` 地址、`-d` 调试模式。  
环境变量：`HAIHUISHOU_UI_HOST`、`HAIHUISHOU_UI_PORT`（默认 5050）；`HAIHUISHOU_SECRET_KEY`（Session 密钥，生产环境请设置）。

### 3. 环境变量（可选）

- `HAIHUISHOU_LOGIN_NAME`：登录手机号  
- `HAIHUISHOU_LOGIN_PWD`：登录密码（明文即可，程序会做 MD5）
- `HAIHUISHOU_SSL_VERIFY`：请求对方 API 时是否校验 HTTPS 证书，默认不校验（`0`）；设为 `1` 可恢复校验。

### 4. 命令行子命令

在本项目目录（`haihuishou/`）下执行：

```bash
python3 -m haihuishou.main login
python3 -m haihuishou.main categories
python3 -m haihuishou.main brands 100001
python3 -m haihuishou.main list --brand-ids 100010,100007 --province 320000 --city 320100 --page 1
python3 -m haihuishou.main quote <record_id> <order_id> <actual_price> --remark "备注"
```

### 5. 在代码中调用

```python
from haihuishou import HaihuishouAPI, GrabOrderTool, GrabCondition

api = HaihuishouAPI()
tool = GrabOrderTool(api=api)
tool.step1_login("你的手机号", "你的密码")
```

## 打包成可执行程序

在本项目目录执行：

```bash
cd haihuishou
pip install pyinstaller
pyinstaller haihuishou.spec
```

产物在 `dist/haihuishou`（macOS/Linux）或 `dist/haihuishou.exe`（Windows）。  
也可通过仓库 GitHub Actions 的 **Build Windows** 工作流手动触发，在 Artifacts 中下载 Windows 可执行文件。

### macOS 在其他电脑上打不开时

1. **右键打开**：对可执行文件右键 →「打开」，在弹窗中再点「打开」。
2. **系统设置放行**：系统设置 → 隐私与安全性 →「仍要打开」。

发给别人之前可先去掉隔离属性：

```bash
cd dist
xattr -cr haihuishou
```

## 目录结构

```
haihuishou/
├── README.md
├── requirements.txt
├── launch_haihuishou.py   # 快捷启动入口
├── run                    # shell 启动脚本
├── haihuishou.spec        # PyInstaller 打包配置
├── 需求文档.md
├── data/                  # 价格表示例等数据文件
├── docs/                  # 接口文档
├── dist/                  # 打包产物
├── haihuishou/            # Python 包
│   ├── __init__.py
│   ├── api.py             # 接口封装
│   ├── grab_tool.py       # 抢单流程与条件
│   ├── main.py            # CLI 入口
│   ├── app_ui.py          # Web UI（Flask）
│   ├── run_ui.py          # 启动 Web UI
│   └── templates/
│       └── index.html
└── ...
```

## 注意

- 仅用于学习或经授权的调试，请遵守平台规则与相关法律法规。
- 请勿将账号密码提交到仓库；建议使用环境变量或本地配置。
