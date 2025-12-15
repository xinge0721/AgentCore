@echo off
chcp 65001 >nul
echo ========================================
echo    API密钥配置管理系统
echo ========================================
echo.
echo 正在启动服务器...
echo.

cd /d "%~dp0"

python app.py

pause

