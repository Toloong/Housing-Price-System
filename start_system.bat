@echo off
setlocal EnableDelayedExpansion
chcp 65001 >nul
title 房价分析系统启动器

echo =============================================
echo         房价分析系统 Windows 启动脚本
echo =============================================
echo.

REM 检查Python是否安装
echo 检查Python环境...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python未安装请先安装Python 3.8+
    pause
    exit /b 1
)
echo ✅ Python已安装

REM 检查虚拟环境
echo 检查虚拟环境...
if exist ".venv" (
    echo ✅ 虚拟环境已存在
) else (
    echo 📦 创建虚拟环境...
    python -m venv .venv
    if %errorlevel% neq 0 (
        echo ❌ 虚拟环境创建失败
        pause
        exit /b 1
    )
    echo ✅ 虚拟环境创建成功
)

REM 激活虚拟环境
echo 激活虚拟环境...
call .venv\Scripts\activate.bat
if %errorlevel% neq 0 (
    echo ❌ 虚拟环境激活失败
    pause
    exit /b 1
)
echo ✅ 虚拟环境已激活

REM 检查依赖包
echo 检查依赖包...
python -c "import fastapi, uvicorn, streamlit" >nul 2>&1
if %errorlevel% neq 0 (
    echo 📦 安装依赖包...
    pip install -r requirements.txt
    if %errorlevel% neq 0 (
        echo ❌ 依赖包安装失败
        pause
        exit /b 1
    )
    echo ✅ 依赖包安装成功
) else (
    echo ✅ 依赖包已安装
)

REM 检查数据库连接
echo 检查数据库连接...
python -c "import psycopg2; psycopg2.connect('postgresql://Housing_Price_postgres:123456@localhost/Housing_Price_postgres').close()" >nul 2>&1
if %errorlevel% eq 0 (
    echo ✅ 数据库连接正常
) else (
    echo ⚠️  数据库连接失败，用户管理功能将不可用
    echo    如需使用用户管理功能，请运行: python init_database.py
)

echo.
echo =============================================
echo             系统启动
echo =============================================
echo.
echo 请选择启动方式:
echo 1. 自动启动 ^(推荐^) - 自动打开新窗口启动前后端
echo 2. 仅启动后端 - 手动在另一个终端启动前端  
echo 3. 仅启动前端 - 需要后端已在运行
echo 4. 退出
echo.

set /p choice=请输入选择 ^(1-4^): 

if "%choice%"=="1" goto start_both
if "%choice%"=="2" goto start_backend
if "%choice%"=="3" goto start_frontend
if "%choice%"=="4" goto exit_script
echo ❌ 无效选择，退出
pause
exit /b 1

:start_both
echo 🚀 自动启动前后端...
echo.
echo 启动后端服务...

REM 启动后端 - 在新窗口中
start "房价分析系统 - 后端服务" cmd /k "call .venv\Scripts\activate.bat && echo Backend starting... && echo Access: http://localhost:8000 && echo API Docs: http://localhost:8000/docs && uvicorn backend.main:app --reload --port 8000"

REM 等待后端启动
echo 等待后端启动...
timeout /t 3 /nobreak >nul

echo 启动前端应用...

REM 启动前端 - 在新窗口中  
start "房价分析系统 - 前端应用" cmd /k "call .venv\Scripts\activate.bat && echo Frontend starting... && echo Access: http://localhost:8501 && streamlit run frontend/app.py"

echo.
echo ✅ 系统启动完成!
echo 前端应用: http://localhost:8501
echo 后端API: http://localhost:8000  
echo API文档: http://localhost:8000/docs
echo.
echo 按任意键关闭此窗口...
pause >nul
exit /b 0

:start_backend
echo 🔧 启动后端服务...
echo 访问地址: http://localhost:8000
echo API文档: http://localhost:8000/docs
echo.
echo 请在另一个终端运行前端:
echo   .venv\Scripts\activate
echo   streamlit run frontend/app.py
echo.
uvicorn backend.main:app --reload --port 8000
goto end

:start_frontend
echo 🎨 启动前端应用...
echo 应用将在浏览器中自动打开
echo.
streamlit run frontend/app.py
goto end

:exit_script
echo 👋 退出启动脚本
exit /b 0

:end
pause
