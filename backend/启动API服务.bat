@echo off
chcp 65001 >nul
echo ========================================
echo 启动颍上小智 API 服务
echo ========================================
echo.
cd /d "%~dp0api"
echo 当前目录: %cd%
echo.
echo 第一步：安装依赖（如已安装可跳过）
pip install flask flask-cors requests python-dotenv -q
echo.
echo 第二步：启动服务（按Ctrl+C停止）
echo 服务地址: http://localhost:5000
echo.
python ys_api_server.py
pause
