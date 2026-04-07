# Codex Usage Tag Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 将上游 `bbtag` 代码引入当前仓库，并提供正式可运行的 2.13 寸 Codex usage 推送命令。

**Architecture:** 当前仓库直接承载 `bluetag` 包和示例文件；将 `examples/push_codex_usage.py` 重构为对包内 `bluetag.codex_usage` 的薄封装，避免双份实现。自动化测试只覆盖纯 Python 逻辑，BLE 和真实设备推送用本机手工验证。

**Tech Stack:** Python 3.10+, uv, Pillow, bleak, python-lzo, pytest

---

### Task 1: 整合上游代码并建立测试基线

**Files:**
- Modify: `README.md`
- Create: `tests/test_codex_usage.py`
- Modify: `pyproject.toml`

- [ ] **Step 1: 写一个失败测试，约束正式 CLI 模块存在且能导入**

```python
from bluetag import codex_usage


def test_module_has_main():
    assert callable(codex_usage.main)
```

- [ ] **Step 2: 运行测试，确认先失败**

Run: `uv run --with pytest pytest tests/test_codex_usage.py -k module_has_main -v`
Expected: FAIL，提示 `bluetag.codex_usage` 不存在

- [ ] **Step 3: 引入上游代码并添加正式模块骨架**

```python
def main() -> int:
    return 0
```

- [ ] **Step 4: 再次运行测试，确认转绿**

Run: `uv run --with pytest pytest tests/test_codex_usage.py -k module_has_main -v`
Expected: PASS

- [ ] **Step 5: 提交阶段性变更**

```bash
git add .
git commit -m "feat: import bbtag upstream and add codex usage entrypoint"
```

### Task 2: 迁移 Codex usage 逻辑并保留示例入口

**Files:**
- Create: `bluetag/codex_usage.py`
- Modify: `examples/push_codex_usage.py`
- Test: `tests/test_codex_usage.py`

- [ ] **Step 1: 写失败测试，覆盖 URL 解析与 usage 行构造**

```python
def test_build_rows_supports_primary_and_secondary_windows():
    payload = {
        "usage": {
            "primary": {"used_percent": 25, "limit_window_seconds": 18000},
            "secondary": {"used_percent": 40, "limit_window_seconds": 604800},
        }
    }
    rows = codex_usage.build_rows(payload, timezone.utc)
    assert [row.label for row in rows] == ["5h limit", "weekly limit"]
```

- [ ] **Step 2: 运行测试，确认先失败**

Run: `uv run --with pytest pytest tests/test_codex_usage.py -k primary_and_secondary -v`
Expected: FAIL，提示逻辑未实现

- [ ] **Step 3: 迁移完整逻辑到 `bluetag.codex_usage`，示例脚本只调用 `main()`**

```python
from bluetag.codex_usage import main


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 4: 运行目标测试，确认通过**

Run: `uv run --with pytest pytest tests/test_codex_usage.py -v`
Expected: PASS

- [ ] **Step 5: 提交阶段性变更**

```bash
git add bluetag/codex_usage.py examples/push_codex_usage.py tests/test_codex_usage.py
git commit -m "feat: promote codex usage example to first-class cli"
```

### Task 3: 补全文档并做本机验证

**Files:**
- Modify: `README.md`

- [ ] **Step 1: 更新 README，明确 2.13 寸扫描与推送命令**

```markdown
uv run bluetag scan --screen 2.13inch
uv run bluetag-codex-usage --preview-only
uv run bluetag-codex-usage --device EDP-XXXX
```

- [ ] **Step 2: 运行完整测试**

Run: `uv run --with pytest pytest -q`
Expected: PASS

- [ ] **Step 3: 运行预览验证**

Run: `uv run bluetag-codex-usage --preview-only`
Expected: 生成 `codex-usage-2.13inch.png`

- [ ] **Step 4: 运行设备扫描**

Run: `uv run bluetag scan --screen 2.13inch`
Expected: 发现 `EDP-` 设备，或明确给出扫描失败原因

- [ ] **Step 5: 尝试真实推送**

Run: `uv run bluetag-codex-usage`
Expected: 成功推送，或输出真实阻塞点（例如蓝牙权限、依赖、设备连接）
