@echo off
chcp 65001 >nul
echo ========================================
echo 启动颍上小智 API 服务
echo ========================================
echo.
cd /d "d:\yingxiao-ai\资料收集"
echo 当前目录: %cd%
echo.
echo 第一步：安装依赖（如已安装可跳过）
pip install flask flask-cors requests -q
echo.
echo 第二步：启动服务（按Ctrl+C停止）
python ys_api_server.py
pause
