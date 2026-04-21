# BluETag

BT370R 蓝签电子墨水标签 BLE 图像推送库。

支持两类屏幕:

- `3.7inch` (`240×416`, 4 色, 设备名前缀 `EPD-`)
- `2.13inch` (`250×122`, 黑/白/红, 设备名前缀 `EDP-`)

CLI 会按 `--screen` 自动切换发送协议，并分别缓存到 `.device.3.7inch` / `.device.2.13inch`。默认屏幕是 `3.7inch`。

## 快速开始

```bash
# 系统依赖
# macOS: brew install lzo
# Linux: sudo apt install liblzo2-dev

# 安装
git clone <your-repo-url> && cd bbtag

# macOS (Homebrew): python-lzo 需要显式指向 Homebrew 的 lzo 头文件
LZO_DIR="$(brew --prefix lzo)" uv sync

# Linux
uv sync
```

如果本机没有 `uv`，也可以直接用 Python 3.13 虚拟环境:

```bash
/opt/homebrew/bin/python3.13 -m venv .venv
LZO_DIR="$(brew --prefix lzo)" .venv/bin/pip install -e .
```

如果 macOS 上看到 `fatal error: 'lzo/lzo1.h' file not found`，说明 `python-lzo`
没有找到 Homebrew 的 `lzo` 头文件；使用上面的 `LZO_DIR=... uv sync` 即可。

需要蓝牙适配器 (USB dongle 或内置蓝牙)。

### WSL 说明

- `bluetag-codex-usage` 在 WSL 下会先查当前 Linux 侧的 `CODEX_HOME` / `~/.codex`，如果检测到 WSL，也会顺带搜索 `/mnt/c/Users/*/.codex`。
- 如果找到 ChatGPT OAuth 登录态，会请求 `https://chatgpt.com/backend-api/wham/usage` 显示真正的 quota。
- 如果当前只有 API key 登录态，ChatGPT usage 接口不可用，脚本会自动退回到本地 `sessions` 汇总并生成 `codex local` 预览。
- 蓝牙发送仍依赖 Python `bleak` 和当前 Linux 环境可用的 BLE 栈。也就是说，WSL 里能否真正推送，取决于你的 WSL 是否已经具备可工作的 Linux 蓝牙访问；仓库当前没有内置 Windows BLE 桥接。

### WSL 蓝牙桥接

如果你在 Windows 上使用 USB 蓝牙适配器，可以用 `usbipd-win` 把这块 USB 设备交给 WSL，再在 Ubuntu 里用 `bluetoothctl` 控制。

仓库里提供了一个 helper:

```bash
# 看当前 usbipd / WSL 蓝牙状态
scripts/wsl-bluetooth status

# 自动找到 "Bluetooth Radio" 并 attach 到当前 WSL distro
scripts/wsl-bluetooth attach

# attach 后直接扫描附近设备
scripts/wsl-bluetooth scan

# 用完后把 USB 蓝牙适配器还给 Windows
scripts/wsl-bluetooth detach
```

这个脚本会调用：

- Windows 侧的 `usbipd-win`
- `wsl.exe -u root`
- Ubuntu 里的 `systemctl` / `bluetoothctl`

注意：

- 设备 attach 到 WSL 期间，Windows 不能同时使用这块蓝牙适配器。
- 某些 CSR 兼容适配器，尤其是 `VID:PID 0a12:0001`，即使 attach 成功，也可能在 Linux 里卡在 `CSR: Local version failed (-110)`，这属于适配器/驱动兼容性问题，不是脚本逻辑问题。

## CLI

```bash
# 扫描设备
uv run bluetag scan

# 扫描 2.13 寸设备
uv run bluetag scan --screen 2.13inch

# 推送图片
uv run bluetag push photo.png

# 推送到 2.13 寸
uv run bluetag push photo.png --screen 2.13inch

# 推送文字 (自动排版)
uv run bluetag text "14:00 项目评审\n16:00 周会"

# 给 2.13 寸推送文字
uv run bluetag text "会议室A\n14:00-15:30" --screen 2.13inch

# 把 Codex usage 画成 /stats 风格并推到 2.13 寸
uv run bluetag-codex-usage

# 仅生成 Codex usage 预览图
uv run bluetag-codex-usage --preview-only

# 指定目标 2.13 寸设备
uv run bluetag-codex-usage --device EDP-F3F4F5F6

# WSL 下先验证 quota / session 预览，不推送
uv run bluetag-codex-usage --preview-only

# 兼容旧入口
uv run examples/push_codex_usage.py --preview-only

# 把 Kimi Code usage 画成 /stats 风格并推到 2.13 寸
uv run examples/push_kimi_usage.py

# 把 Kimi Code usage 画成 /stats 风格并推到 3.7 寸
uv run examples/push_kimi_usage_3.7.py

# 把 macOS 当天 App 使用时长榜单推到 3.7 寸
# 需要给终端 Full Disk Access 才能读取 Knowledge 数据库
uv run examples/push_macos_app_usage_3.7.py --preview-only

# 仅生成 Kimi usage 预览图
uv run examples/push_kimi_usage.py --preview-only

# 自定义标题和颜色
uv run bluetag text "会议室A 三楼" --title "指引" --title-color red

# 仅生成预览图，不推送
uv run bluetag text "测试内容" --preview-only

# 指定 3.7 寸设备
uv run bluetag push photo.png -d EPD-EBB9D76B

# 指定 2.13 寸设备
uv run bluetag push photo.png --screen 2.13inch -d EDP-F3F4F5F6

# 调整发送速度 (ms/包, 默认按屏幕选择)
uv run bluetag push photo.png -i 80
```

### text 子命令参数

| 参数 | 说明 |
|------|------|
| `body` (位置参数) | 正文内容，`\n` 换行 |
| `--title, -T` | 标题，默认当天日期，格式 `YYYY-MM-DD` |
| `--title-color` | 标题颜色: black / red / yellow |
| `--body-color` | 正文颜色: black / red / yellow |
| `--separator-color` | 分隔线颜色: black / red / yellow |
| `--align` | 正文对齐: left / center |
| `--font` | 自定义字体路径 |
| `--preview-only` | 仅生成预览图，不推送 |
| `--screen` | 屏幕尺寸: `3.7inch` / `2.13inch` |

文字排版会根据 `--screen` 自动切换画布尺寸和字号策略。标题尽量大 (最多 2 行)，正文自动缩小直到全部放得下。

## Python API

```python
import asyncio
from PIL import Image
from bluetag import quantize, pack_2bpp, build_frame, packetize, render_text
from bluetag.protocol import parse_mac_suffix
from bluetag.ble import scan, push

async def push_image():
    img = Image.open("photo.png")
    indices = quantize(img)
    data_2bpp = pack_2bpp(indices)

    devices = await scan()
    target = devices[0]
    mac = parse_mac_suffix(target["name"])
    frame = build_frame(mac, data_2bpp)
    packets = packetize(frame)
    await push(packets, device_address=target["address"])

async def push_text():
    img = render_text(body="Hello World", title="2026-03-30")
    indices = quantize(img)
    data_2bpp = pack_2bpp(indices)

    devices = await scan()
    target = devices[0]
    mac = parse_mac_suffix(target["name"])
    frame = build_frame(mac, data_2bpp)
    packets = packetize(frame)
    await push(packets, device_address=target["address"])

asyncio.run(push_image())
```

## 项目结构

```
bbtag/
├── bluetag/              # Python 核心库
│   ├── image.py          #   图像量化、2bpp 编解码
│   ├── text.py           #   文字渲染、自动排版
│   ├── protocol.py       #   协议帧组装、LZO 压缩、分包
│   ├── ble.py            #   BLE 扫描/连接/发送 (bleak)
│   ├── screens.py        #   屏幕配置、设备名前缀、缓存文件规则
│   ├── transfer.py       #   2.13 寸图层发送协议
│   ├── server.py         #   REST API 服务 (FastAPI)
│   ├── cli.py            #   命令行工具
│   └── codex_usage.py    #   Codex usage 正式 CLI 入口
├── examples/                     # 示例脚本
│   ├── push_image.py             #   推送图片示例
│   ├── push_text.py              #   推送文字示例
│   ├── push_codex_usage.py       #   Codex usage -> 2.13 寸
│   ├── push_codex_usage_3.7.py   #   Codex usage -> 3.7 寸
│   ├── push_kimi_usage.py        #   Kimi usage -> 2.13 寸
│   ├── push_kimi_usage_3.7.py    #   Kimi usage -> 3.7 寸
│   └── push_macos_app_usage_3.7.py # macOS app usage -> 3.7 寸
└── pyproject.toml
```

## 运维索引

- Windows 定时推送与手工触发说明：`docs/windows-codex-usage-scheduler.md`
- 当前默认计划任务：`bbtag-codex-usage-30min`（已配置为每 10 分钟执行一次）
