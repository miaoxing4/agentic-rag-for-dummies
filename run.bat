@echo off
chcp 65001 >nul
set PYTHONIOENCODING=utf-8
echo ========================================
echo       O-RAN 问题诊断助手启动脚本
echo ========================================
echo.

cd /d "%~dp0"

echo [1/2] 激活虚拟环境...
call venv\Scripts\activate.bat

if errorlevel 1 (
    echo [错误] 虚拟环境激活失败，请检查 venv 目录是否存在
    pause
    exit /b 1
)

echo [2/2] 启动应用...
python project\app.py

pause
