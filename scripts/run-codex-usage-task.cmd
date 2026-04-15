@echo off
setlocal

cd /d C:\Users\xin.yan\work\bbtag
set "PYTHONUTF8=1"
set "PYTHONIOENCODING=utf-8"

if not exist ".venv-win\Scripts\python.exe" (
  echo [ERR] Missing Python runtime: .venv-win\Scripts\python.exe
  exit /b 2
)

".venv-win\Scripts\python.exe" -m bluetag.codex_usage --auth-path ".\codex_oauth_info\auth.json" --config-path ".\codex_oauth_info\config.toml"
exit /b %ERRORLEVEL%
