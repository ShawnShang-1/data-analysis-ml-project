@echo off
chcp 65001 >nul
cd /d "%~dp0"

echo ============================================================
echo   Wav2Lip 推理服务启动
echo   端口: 8001
echo ============================================================
echo.

python wav2lip_server.py --port 8001 --host 0.0.0.0

pause