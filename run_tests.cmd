@echo off
setlocal
set PYTHONUNBUFFERED=1
cd /d "%~dp0"

if exist "%LOCALAPPDATA%\esphome-venv\Scripts\python.exe" (
    set "PY_BIN=%LOCALAPPDATA%\esphome-venv\Scripts\python.exe"
) else if exist "%USERPROFILE%\esphome-venv\Scripts\python.exe" (
    set "PY_BIN=%USERPROFILE%\esphome-venv\Scripts\python.exe"
) else if exist "%VIRTUAL_ENV%\Scripts\python.exe" (
    set "PY_BIN=%VIRTUAL_ENV%\Scripts\python.exe"
) else (
    set "PY_BIN=python"
)


"%PY_BIN%" -u run_tests.py %*
