@echo off
echo 房价分析系统 - 环境安装脚本
echo ============================
echo.

echo [1/4] 检查Python环境...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python未安装或未添加到PATH，请先安装Python 3.8+
    pause
    exit /b 1
)
echo ✓ Python环境正常

echo.
echo [2/4] 创建虚拟环境...
if exist ".venv" (
    echo ⚠ 虚拟环境已存在，跳过创建
) else (
    python -m venv .venv
    if %errorlevel% neq 0 (
        echo ❌ 虚拟环境创建失败
        pause
        exit /b 1
    )
    echo ✓ 虚拟环境创建成功
)

echo.
echo [3/4] 激活虚拟环境并安装依赖...
call .venv\Scripts\activate.bat
if %errorlevel% neq 0 (
    echo ❌ 虚拟环境激活失败
    pause
    exit /b 1
)

echo ✓ 虚拟环境已激活
echo 正在安装Python依赖包...
pip install --upgrade pip
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ❌ 依赖安装失败
    pause
    exit /b 1
)

echo.
echo [4/4] 初始化数据库...
python -c "from backend.database import init_sqlite_database; init_sqlite_database(); print('✓ 数据库初始化完成')"

echo.
echo ✅ 环境安装完成！
echo.
echo 🚀 现在可以运行 start.bat 启动系统
echo.
pause
