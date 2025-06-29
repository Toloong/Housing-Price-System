@echo off
echo 启动房价分析系统...
echo.

echo [0/3] 设置PowerShell执行策略并激活虚拟环境...
powershell -Command "Set-ExecutionPolicy RemoteSigned -Scope Process; .\.venv\Scripts\Activate.ps1; Write-Host '✓ 虚拟环境已激活'"

echo [1/3] 启动后端服务 (FastAPI)...
start "FastAPI Backend" cmd /c "cd /d %~dp0 && .\.venv\Scripts\activate && python -m uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000"

echo [2/3] 启动前端服务 (Streamlit)...
timeout /t 5 >nul
start "Streamlit Frontend" cmd /c "cd /d %~dp0 && .\.venv\Scripts\activate && streamlit run frontend/app.py --server.port 8501"

echo.
echo ✅ 系统启动完成!
echo 📊 前端地址: http://localhost:8501
echo 🔧 后端API: http://localhost:8000
echo.
echo 💡 提示: 如果虚拟环境不存在，请先运行以下命令创建：
echo    python -m venv .venv
echo    .\.venv\Scripts\activate
echo    pip install -r requirements.txt
echo.
pause
