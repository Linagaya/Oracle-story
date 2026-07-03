@echo off
echo ================================
echo 甲骨文AI识别系统 - 启动脚本
echo ================================
echo.
echo 正在检查必要目录...
if not exist "%~dp0data\training\train" mkdir "%~dp0data\training\train"
if not exist "%~dp0data\training\val" mkdir "%~dp0data\training\val"
if not exist "%~dp0data\test" mkdir "%~dp0data\test"
if not exist "%~dp0backend\model" mkdir "%~dp0backend\model"
echo 目录检查完成。
echo.
echo 正在启动后端服务...
cd /d "%~dp0backend"
pip install -r requirements.txt
echo.
echo 启动FastAPI服务器...
echo 服务地址: http://localhost:8000
echo API文档: http://localhost:8000/docs
echo.
python main.py
pause