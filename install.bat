@echo off
chcp 65001 >nul
title 房价分析系统 - Windows一键安装

echo.
echo    ██╗  ██╗ ██████╗ ██╗   ██╗███████╗██╗███╗   ██╗ ██████╗ 
echo    ██║  ██║██╔═══██╗██║   ██║██╔════╝██║████╗  ██║██╔════╝ 
echo    ███████║██║   ██║██║   ██║███████╗██║██╔██╗ ██║██║  ███╗
echo    ██╔══██║██║   ██║██║   ██║╚════██║██║██║╚██╗██║██║   ██║
echo    ██║  ██║╚██████╔╝╚██████╔╝███████║██║██║ ╚████║╚██████╔╝
echo    ╚═╝  ╚═╝ ╚═════╝  ╚═════╝ ╚══════╝╚═╝╚═╝  ╚═══╝ ╚═════╝ 
echo.
echo    ██████╗ ██████╗ ██╗ ██████╗███████╗
echo    ██╔══██╗██╔══██╗██║██╔════╝██╔════╝
echo    ██████╔╝██████╔╝██║██║     █████╗  
echo    ██╔═══╝ ██╔══██╗██║██║     ██╔══╝  
echo    ██║     ██║  ██║██║╚██████╗███████╗
echo    ╚═╝     ╚═╝  ╚═╝╚═╝ ╚═════╝╚══════╝
echo.
echo         房价分析系统 v3.0 - Windows一键安装程序
echo    ===================================================
echo.

REM 检查是否在正确的目录
if not exist "requirements.txt" (
    echo ❌ 错误：请在项目根目录下运行此脚本
    echo    当前目录应包含 requirements.txt 文件
    echo.
    pause
    exit /b 1
)

echo 🚀 欢迎使用房价分析系统！
echo.
echo 本程序将为您自动完成以下操作：
echo   ✓ 检查并安装Python依赖
echo   ✓ 创建虚拟环境  
echo   ✓ 配置数据库（可选）
echo   ✓ 启动应用系统
echo.

set /p confirm=是否继续安装？ (Y/N): 
if /i not "%confirm%"=="Y" (
    echo 👋 安装已取消
    pause
    exit /b 0
)

echo.
echo ====================================================
echo                   开始安装
echo ====================================================
echo.

REM 检查Python
echo 🐍 检查Python环境...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python未安装
    echo.
    echo 📥 请先安装Python：
    echo    1. 访问 https://python.org
    echo    2. 下载Python 3.8或更高版本
    echo    3. 安装时勾选"Add to PATH"
    echo    4. 重新运行此脚本
    echo.
    pause
    exit /b 1
)

for /f "tokens=2" %%a in ('python --version 2^>^&1') do set python_version=%%a
echo ✅ Python已安装: %python_version%

REM 创建虚拟环境
echo.
echo 📦 设置虚拟环境...
if exist ".venv" (
    echo ✅ 虚拟环境已存在
) else (
    echo 🔧 创建虚拟环境...
    python -m venv .venv
    if %errorlevel% neq 0 (
        echo ❌ 虚拟环境创建失败
        pause
        exit /b 1
    )
    echo ✅ 虚拟环境创建成功
)

REM 激活虚拟环境
echo 🔌 激活虚拟环境...
call .venv\Scripts\activate.bat
if %errorlevel% neq 0 (
    echo ❌ 虚拟环境激活失败
    pause
    exit /b 1
)
echo ✅ 虚拟环境已激活

REM 安装依赖
echo.
echo 📚 安装项目依赖...
echo    这可能需要几分钟时间，请耐心等待...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ❌ 依赖安装失败
    echo.
    echo 💡 可能的解决方案：
    echo    1. 检查网络连接
    echo    2. 升级pip: python -m pip install --upgrade pip
    echo    3. 使用国内镜像: pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
    echo.
    pause
    exit /b 1
)
echo ✅ 依赖安装完成

REM 数据库配置选择
echo.
echo ====================================================
echo                  数据库配置
echo ====================================================
echo.
echo 🔐 用户管理功能需要PostgreSQL数据库支持
echo.
echo 选择操作：
echo   1. 配置PostgreSQL（推荐，支持完整功能）
echo   2. 跳过数据库配置（仅基础功能）
echo.

set /p db_choice=请选择 (1-2): 

if "%db_choice%"=="1" (
    echo.
    echo 🐘 开始配置PostgreSQL...
    
    REM 检查PostgreSQL是否安装
    psql --version >nul 2>&1
    if %errorlevel% neq 0 (
        echo ⚠️  PostgreSQL未检测到
        echo.
        echo 📥 请安装PostgreSQL：
        echo    1. 访问 https://www.postgresql.org/download/windows/
        echo    2. 下载并安装PostgreSQL 12+
        echo    3. 记住postgres用户密码
        echo    4. 重新运行此脚本
        echo.
        set /p skip_db=是否跳过数据库配置继续安装？ (Y/N): 
        if /i "!skip_db!"=="Y" (
            echo ⏭️  跳过数据库配置
        ) else (
            pause
            exit /b 1
        )
    ) else (
        echo ✅ PostgreSQL已安装
        echo 🔧 运行数据库配置脚本...
        
        if exist "setup_postgresql.ps1" (
            powershell -ExecutionPolicy Bypass -File setup_postgresql.ps1
        ) else (
            echo 🔧 手动配置数据库...
            python init_database.py
        )
    )
) else (
    echo ⏭️  跳过数据库配置，将仅提供基础功能
)

REM 安装完成
echo.
echo ====================================================
echo                  安装完成！
echo ====================================================
echo.
echo ✅ 房价分析系统安装成功！
echo.
echo 🌟 功能特性：
echo    • 🏠 房价查询和搜索
echo    • 📈 趋势分析和可视化  
echo    • 🏙️ 城市对比分析
echo    • 🤖 AI智能助手
if "%db_choice%"=="1" (
    echo    • 👥 用户管理系统 ^(已配置^)
) else (
    echo    • 👥 用户管理系统 ^(未配置^)
)
echo.
echo 🚀 现在启动系统？
set /p start_now=立即启动应用 (Y/N): 

if /i "%start_now%"=="Y" (
    echo.
    echo 🎯 启动系统...
    call start_system.bat
) else (
    echo.
    echo 📖 手动启动说明：
    echo    1. 双击 start_system.bat
    echo    2. 或运行 .\start_system.ps1
    echo.
    echo 🌐 访问地址：
    echo    前端应用: http://localhost:8501
    echo    后端API: http://localhost:8000
    echo.
    echo 📚 更多帮助请查看 WINDOWS_GUIDE.md
)

echo.
echo 感谢使用房价分析系统！ 🎉
pause
