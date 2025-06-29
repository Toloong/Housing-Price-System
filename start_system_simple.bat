@echo off
setlocal EnableDelayedExpansion
chcp 65001 >nul
title Housing Price Analysis System Launcher

echo =============================================
echo    Housing Price Analysis System Launcher
echo =============================================
echo.

REM Check Python installation
echo Checking Python environment...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python not installed, please install Python 3.8+
    pause
    exit /b 1
)
echo SUCCESS: Python installed

REM Check virtual environment
echo Checking virtual environment...
if exist ".venv" (
    echo SUCCESS: Virtual environment exists
) else (
    echo Creating virtual environment...
    python -m venv .venv
    if %errorlevel% neq 0 (
        echo ERROR: Failed to create virtual environment
        pause
        exit /b 1
    )
    echo SUCCESS: Virtual environment created
)

REM Activate virtual environment
echo Activating virtual environment...
call .venv\Scripts\activate.bat
if %errorlevel% neq 0 (
    echo ERROR: Failed to activate virtual environment
    pause
    exit /b 1
)
echo SUCCESS: Virtual environment activated

REM Check dependencies
echo Checking dependencies...
python -c "import fastapi, uvicorn, streamlit" >nul 2>&1
if %errorlevel% neq 0 (
    echo Installing dependencies...
    pip install -r requirements.txt
    if %errorlevel% neq 0 (
        echo ERROR: Failed to install dependencies
        pause
        exit /b 1
    )
    echo SUCCESS: Dependencies installed
) else (
    echo SUCCESS: Dependencies already installed
)

REM Check database connection
echo Checking database connection...
python -c "import psycopg2; psycopg2.connect('postgresql://Housing_Price_postgres:123456@localhost/Housing_Price_postgres').close()" >nul 2>&1
if %errorlevel% eq 0 (
    echo SUCCESS: Database connection OK
) else (
    echo WARNING: Database connection failed, user management unavailable
    echo          To use user management: python init_database.py
)

echo.
echo =============================================
echo             System Startup
echo =============================================
echo.
echo Please choose startup option:
echo 1. Auto Start ^(Recommended^) - Open new windows for backend and frontend
echo 2. Backend Only - Manual frontend startup required
echo 3. Frontend Only - Backend must be running
echo 4. Exit
echo.

set /p choice=Enter choice ^(1-4^): 

if "%choice%"=="1" goto start_both
if "%choice%"=="2" goto start_backend
if "%choice%"=="3" goto start_frontend
if "%choice%"=="4" goto exit_script
echo ERROR: Invalid choice, exiting
pause
exit /b 1

:start_both
echo Starting backend and frontend...
echo.
echo Starting backend service...

REM Start backend in new window
start "Housing Price System - Backend" cmd /k "call .venv\Scripts\activate.bat && echo Backend starting... && echo Access: http://localhost:8000 && echo API Docs: http://localhost:8000/docs && uvicorn backend.main:app --reload --port 8000"

REM Wait for backend to start
echo Waiting for backend startup...
timeout /t 3 /nobreak >nul

echo Starting frontend application...

REM Start frontend in new window
start "Housing Price System - Frontend" cmd /k "call .venv\Scripts\activate.bat && echo Frontend starting... && echo Access: http://localhost:8501 && streamlit run frontend/app.py"

echo.
echo SUCCESS: System started!
echo Frontend: http://localhost:8501
echo Backend API: http://localhost:8000  
echo API Docs: http://localhost:8000/docs
echo.
echo Press any key to close this window...
pause >nul
exit /b 0

:start_backend
echo Starting backend service...
echo Access: http://localhost:8000
echo API Docs: http://localhost:8000/docs
echo.
echo To start frontend manually:
echo   .venv\Scripts\activate
echo   streamlit run frontend/app.py
echo.
uvicorn backend.main:app --reload --port 8000
goto end

:start_frontend
echo Starting frontend application...
echo Application will open in browser automatically
echo.
streamlit run frontend/app.py
goto end

:exit_script
echo Exiting startup script
exit /b 0

:end
pause
