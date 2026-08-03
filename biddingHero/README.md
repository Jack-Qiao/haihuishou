# 竞价侠（biddingHero）

基于竞价侠平台接口的报价工具，跟嗨回收工具（haihuishou）功能与界面接近，但数据来源与操作模型不同：

- **无「抢单」按钮**：可以直接在列表中出价（`place_bid`）。
- **查看详情 = 抢单**：调用商品详情 `detail_info` 后，该商品会自动加入到「报价中列表」（`grab_order_list`）。
- **报价数据展示条件**：拿到详情后，再对比「报价中列表」，只有列表里包含此商品的 id 时，才展示商品的报价数据列表详情。

## 接口

- Base URL: `https://jingjiaxia.com`
- 鉴权：登录接口外均使用 `Authorization: Bearer <token>`

| 用途 | 方法 | 路径 |
|---|---|---|
| 登录 | POST | `/api/base/login/` |
| 查询列表 | GET | `/api/base/orders/auction_list/` |
| 报价中列表 | GET | `/api/base/orders/grab_order_list/` |
| 已报价列表 | GET | `/api/base/bid-records/my_bids/` |
| 获取用户信息 | GET | `/api/base/users/getMyInfo/` |
| 商品详情 | GET | `/api/base/orders/{orderId}/detail_info/` |
| 出价 | POST | `/api/base/orders/{orderId}/place_bid/` |
| 取消抢单 | POST | `/api/base/orders/{orderId}/cancel_grab_order/` |

## 环境

- Python 3.8+
- 依赖：`pip install -r requirements.txt`

## 使用

### 启动 Web UI

```bash
cd biddingHero
pip install -r requirements.txt
python3 launch_biddinghero.py
# 或
python3 -m biddinghero.run_ui
```

启动后浏览器访问 **http://127.0.0.1:5070**。  
可选参数：`-p` 端口、`-H` 地址、`-d` 调试模式。  
环境变量：`BIDDINGHERO_UI_HOST`、`BIDDINGHERO_UI_PORT`（默认 5070）；`BIDDINGHERO_SECRET_KEY`（Session 密钥）。

### CLI

```bash
python3 -m biddinghero.main --phone 手机号 --password 密码 list
python3 -m biddinghero.main --phone 手机号 --password 密码 detail 9493974
python3 -m biddinghero.main --phone 手机号 --password 密码 bid 9493974 100
python3 -m biddinghero.main --phone 手机号 --password 密码 grab-list
python3 -m biddinghero.main --phone 手机号 --password 密码 my-bids
```

## 打包

```bash
pip install pyinstaller
pyinstaller biddinghero.spec
```

产物在 `dist/biddinghero`（macOS/Linux）或 `dist/biddinghero.exe`（Windows）。

## 目录结构

```
biddingHero/
├── README.md
├── requirements.txt
├── launch_biddinghero.py     # 快捷启动
├── biddinghero.spec          # PyInstaller 打包配置
├── 需求文档.md
├── 接口文档说明               # 平台接口原始文档
└── biddinghero/              # Python 包
    ├── __init__.py
    ├── api.py                # 竞价侠 API 封装
    ├── main.py               # CLI
    ├── app_ui.py             # Web UI (Flask)
    ├── run_ui.py
    └── templates/
        └── index.html
```

## 与 haihuishou 的差异

| 维度 | haihuishou | biddingHero（竞价侠） |
|---|---|---|
| 域名 | hsdapi.haihuishou.com | jingjiaxia.com |
| 鉴权头 | `token: <token>` | `Authorization: Bearer <token>` |
| 操作模型 | 先抢单再报价 | 直接出价，无需先抢单 |
| 详情语义 | 只查看 | 查看详情即「抢单」，商品进入报价中列表 |
| 报价明细 | 详情直接可读 | 仅当商品在报价中列表时才展示报价数据列表详情 |
