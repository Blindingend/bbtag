# Codex Usage Tag Design

## Goal

将上游 `bbtag` 仓库整合到当前项目中，保留其 2.13 寸蓝牙墨水屏推送能力，并把 Codex usage 推送整理成当前仓库里的正式、可运行入口，而不是仅停留在示例脚本。

## Scope

- 引入上游 `bluetag` 核心库、CLI、示例和依赖定义。
- 将 `examples/push_codex_usage.py` 提炼为包内正式 CLI 入口。
- 保留示例脚本，改为薄封装，避免逻辑重复。
- 补充最小自动化测试，覆盖不依赖 BLE 和网络的核心行为。
- 更新 README，给出 2.13 寸设备扫描和 Codex usage 推送的实际命令。

## Architecture

仓库根目录直接承载上游项目代码，而不是用 submodule。当前仓库几乎为空，直接整合比 submodule 更适合后续本地修改、安装和运行，也避免睡醒后还要递归初始化子模块。

Codex usage 逻辑放入 `bluetag/codex_usage.py`，由 `pyproject.toml` 暴露一个正式可执行入口。示例文件 `examples/push_codex_usage.py` 只保留一层导入和 `main()` 调用，确保命令行和示例两条使用路径都可用。

## Data Flow

1. 从 `~/.codex/auth.json` 与 `~/.codex/config.toml` 读取认证和基础 URL。
2. 拉取 `/wham/usage` JSON，解析主窗口和次窗口使用率。
3. 生成适配 2.13 寸标签的 250x122 预览图。
4. 若不是 `--preview-only`，则扫描 `EDP-` 设备并通过 BLE 发送黑/红两层数据。

## Error Handling

- 缺少认证文件、JSON 非法、API 返回异常时，返回明确错误信息。
- BLE 依赖未安装、扫描不到设备、连接失败时，命令退出并输出原因。
- 若只需要预览，不依赖 BLE。

## Testing

- 覆盖 base URL 解析与安全约束。
- 覆盖 usage payload 解析和行数据构造。
- 覆盖预览图生成和示例包装入口的基本可用性。
- 真实 BLE 扫描/推送只做本机手工验证，不纳入自动化测试。
