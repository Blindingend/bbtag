# Windows Codex Usage 定时推送手册

## 目标

每 30 分钟自动执行一次：

1. 拉取 Codex quota（`/wham/usage`）
2. 生成 `codex-usage-2.13inch.png`
3. 推送到附近 2.13 寸蓝牙标签（`EDP-*`）

## 当前配置

- 任务名：`bbtag-codex-usage-30min`
- 触发方式：每 `30` 分钟
- 执行脚本：[scripts/run-codex-usage-task.cmd](/C:/Users/xin.yan/work/bbtag/scripts/run-codex-usage-task.cmd)
- Python：`C:\Users\xin.yan\work\bbtag\.venv-win\Scripts\python.exe`
- OAuth 配置目录：`C:\Users\xin.yan\work\bbtag\codex_oauth_info`

脚本实际执行命令：

```powershell
.\.venv-win\Scripts\python.exe -m bluetag.codex_usage --auth-path .\codex_oauth_info\auth.json --config-path .\codex_oauth_info\config.toml
```

## 常用命令

查询任务状态：

```powershell
schtasks /Query /TN "bbtag-codex-usage-30min" /V /FO LIST
```

手动触发一次：

```powershell
schtasks /Run /TN "bbtag-codex-usage-30min"
```

临时禁用：

```powershell
schtasks /Change /TN "bbtag-codex-usage-30min" /DISABLE
```

重新启用：

```powershell
schtasks /Change /TN "bbtag-codex-usage-30min" /ENABLE
```

删除任务：

```powershell
schtasks /Delete /TN "bbtag-codex-usage-30min" /F
```

## 从零重建任务

```powershell
schtasks /Create /TN "bbtag-codex-usage-30min" /SC MINUTE /MO 30 /TR "cmd.exe /c C:\Users\xin.yan\work\bbtag\scripts\run-codex-usage-task.cmd" /F
```

## 故障排查

`No Bluetooth adapter found`：

- 先检查是否被 `usbipd` 占用：

```powershell
usbipd list
```

- 若蓝牙 dongle 为 `Attached`（给 WSL），先切回 Windows：

```powershell
usbipd detach --busid <BUSID>
```

`401/403`（quota 拉取失败）：

- `codex_oauth_info/auth.json` 的 token 过期或失效，需要重新做 Codex OAuth 登录。
- 登录完成后确认 `auth.json` 中 access token 未过期，再重跑任务。

## 安全约束

- `codex_oauth_info/` 是本地敏感目录，必须忽略，不要提交到远端。
- 本仓库 `.gitignore` 已包含 `codex_oauth_info/` 规则。
