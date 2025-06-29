@echo off
chcp 65001 >nul
echo Starting Housing Price Analysis System...
echo.

echo [0/3] Setting up environment...
if exist ".venv\Scripts\activate.bat" (
    echo Virtual environment found
) else (
    echo Virtual environment not found, please run setup.bat first
    pause
    exit /b 1
)

echo [1/3] Starting backend service (FastAPI)...
start "FastAPI Backend" cmd /c "cd /d %~dp0 && .\.venv\Scripts\activate && python -m uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000"

echo [2/3] Starting frontend service (Streamlit)...
timeout /t 5 >nul
start "Streamlit Frontend" cmd /c "cd /d %~dp0 && .\.venv\Scripts\activate && streamlit run frontend/app.py --server.port 8501"

echo.
echo System startup complete!
echo Frontend: http://localhost:8501
echo Backend API: http://localhost:8000
echo.
echo Tip: If virtual environment doesn't exist, run setup.bat first
echo.
pause
