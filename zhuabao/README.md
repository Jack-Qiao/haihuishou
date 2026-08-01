# 微信小程序数据抓取（抓包）

在 `zhuabao` 目录下通过 **代理抓包** 方式抓取微信小程序的接口请求与响应数据。

## 原理

1. 本机启动 mitmproxy 代理（默认 8080 端口）。
2. 将 **微信** 或 **系统** 的 HTTP(S) 代理指向本机 8080。
3. 打开目标小程序并操作，流量经代理时由插件记录请求/响应，按天保存为 `wechat_capture/capture_YYYYMMDD.jsonl`。
4. 使用 `export_data.py` 查看统计或导出为 JSON。

## 环境

- Python 3.8+
- 安装依赖：`pip install -r requirements.txt`

## 使用步骤

### 1. 安装根证书（首次必须）

mitmproxy 需要解密 HTTPS，因此本机必须信任其 CA 证书：

```bash
# 启动一次 mitmproxy 后，证书会生成在默认目录，例如：
# macOS: ~/.mitmproxy/mitmproxy-ca-cert.pem
# 用钥匙串访问打开该 .pem，添加到「系统」并设为「始终信任」
```

或先运行一次 `mitmdump -p 8080`，然后按 [mitmproxy 文档](https://docs.mitmproxy.org/stable/concepts-certificates/) 安装证书。

### 2. 启动抓包

```bash
cd zhuabao
pip install -r requirements.txt
python run_capture.py
```

或直接：

```bash
mitmdump -p 8080 -s capture_addon.py
```

### 3. 配置代理（不用 Proxifier 的做法）

- **macOS（推荐：系统代理，无需额外软件）**  
  1. 打开 **系统设置** → **网络** → 点当前连接（Wi‑Fi 或以太网）右侧的 **详细信息…**  
  2. 选 **代理**，勾选 **网页代理 (HTTP)** 和 **安全网页代理 (HTTPS)**  
  3. 两项都填：**服务器** `127.0.0.1`，**端口** `8080`，确定保存  
  4. 此时本机所有 HTTP/HTTPS 流量（包括微信）都会走抓包代理  
  **抓包结束后**：回到同一位置，取消勾选上述两个代理，避免影响正常上网。

- **Windows（抓 PC 版微信）**  
  - **方式 A**：系统代理 — 设置 → 网络和 Internet → 代理 → 手动设置代理，地址 `127.0.0.1`，端口 `8080`（抓完记得关掉）。  
  - **方式 B**：仅让微信走代理，需 Proxifier 等工具，规则里让「微信」或 `WeChatAppEx.exe` 走 `127.0.0.1:8080`。

- **手机**  
  手机与电脑同一 WiFi，WiFi 设置里 HTTP 代理选手动，主机填电脑局域网 IP，端口 8080。电脑需运行 mitmproxy，手机需安装并信任 mitmproxy 的 CA 证书（在手机浏览器访问 `mitm.it` 按提示安装）。

### 4. 打开小程序

在已配置代理的微信中打开目标小程序并正常使用，本机终端会看到流量经过，数据会写入 `wechat_capture/capture_YYYYMMDD.jsonl`。

### 5. 查看与导出数据

**以下命令需在 `zhuabao` 目录下执行**（先执行 `cd zhuabao`）：

```bash
cd zhuabao

# 列出抓取文件
python3 export_data.py

# 解析并统计某天抓包（按 host 统计）
python3 export_data.py wechat_capture/capture_20250223.jsonl --by-host

# 导出为 JSON
python3 export_data.py wechat_capture/capture_20250223.jsonl --json out.json
```

每条记录包含：`time`、`method`、`url`、`host`、请求/响应头、请求/响应体（过大时会被截断）。

## 可选：只抓指定域名

编辑 `capture_addon.py`，给 `ALLOWED_HOSTS` 赋值，例如：

```python
ALLOWED_HOSTS = ["api.example.com", "your-miniapp.com"]
```

留空则抓取所有未在 `EXCLUDED_HOSTS` 中的请求。静态资源等可在 `EXCLUDED_HOSTS` 中排除。

## 示例：抓取「嗨回收回收端」小程序

1. **安装依赖与证书**  
   在 `zhuabao` 下执行 `pip install -r requirements.txt`，并按上文「安装根证书」完成证书安装（否则小程序请求无法解密）。

2. **启动抓包**  
   终端执行：`python run_capture.py`，保持运行。

3. **配置代理**  
   - **PC 微信**：用 Proxifier 等把「微信」进程的代理设为 `127.0.0.1:8080`。  
   - **或** 系统代理设为 `127.0.0.1:8080`（会代理整个系统流量，用完后记得关掉）。

4. **打开并登录小程序**  
   - 打开微信，在聊天里点击「嗨回收回收端」小程序卡片进入。  
   - 在登录页用聊天里提供的**手机号**和**密码**登录。

5. **正常使用小程序**  
   登录后随意操作（如查看订单、回收相关页面），所有经代理的接口请求会被自动保存到 `wechat_capture/capture_YYYYMMDD.jsonl`。

6. **查看抓到的数据**  
   ```bash
   python export_data.py
   python export_data.py wechat_capture/capture_20250223.jsonl --by-host
   ```
   即可看到该小程序的接口 host、URL 及请求/响应内容（登录、列表等接口都会在里面）。

**说明**：抓包工具只负责记录流量，不会替你登录；账号密码仅用于你在微信里手动登录该小程序，请勿写入代码或提交到仓库。

---

## 注意

- 仅用于学习、调试或经授权的场景，请遵守相关法律法规与平台规则。
- 部分小程序有防抓包（证书校验、代理检测），可能无法解密或无法使用，属正常现象。
- 抓包数据可能含敏感信息，请勿泄露、勿提交到版本库；建议将 `wechat_capture/` 加入 `.gitignore`。

## 目录结构

```
zhuabao/
├── README.md           # 说明
├── requirements.txt    # 依赖
├── capture_addon.py    # mitmproxy 抓包插件
├── run_capture.py      # 启动抓包代理
├── export_data.py      # 解析/导出抓包结果
└── wechat_capture/     # 抓取数据目录（按日期 JSONL）
```
