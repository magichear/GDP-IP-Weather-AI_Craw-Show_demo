@echo off
chcp 65001 >nul
set CLOUD_PATH=use_cloudflare_tunnel.py
set SCRIPT_PATH=Main.py

if not exist "%SCRIPT_PATH%" (
    echo Error: 主程序不存在
    pause
    exit /b 1
)

cloudflared --version >nul 2>&1
if %ERRORLEVEL% equ 0 (
    echo Cloudflared 正常工作，使用穿透功能
    python "%CLOUD_PATH%"
) else (
    echo Cloudflared 未安装，仅本地访问
    python "%SCRIPT_PATH%"
)

echo 程序结束
pause