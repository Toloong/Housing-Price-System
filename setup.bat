@echo off
echo Housing Price Analysis System - Environment Setup
echo ================================================
echo.

echo [1/4] Checking Python environment...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python not installed or not in PATH. Please install Python 3.8+
    pause
    exit /b 1
)
echo OK: Python environment detected

echo.
echo [2/4] Creating virtual environment...
if exist ".venv" (
    echo WARNING: Virtual environment already exists, skipping creation
) else (
    python -m venv .venv
    if %errorlevel% neq 0 (
        echo ERROR: Failed to create virtual environment
        pause
        exit /b 1
    )
    echo OK: Virtual environment created successfully
)

echo.
echo [3/4] Activating virtual environment and installing dependencies...
call .venv\Scripts\activate.bat
if %errorlevel% neq 0 (
    echo ERROR: Failed to activate virtual environment
    pause
    exit /b 1
)

echo OK: Virtual environment activated
echo Installing Python packages...
pip install --upgrade pip
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)

echo.
echo [4/4] Initializing database...
python -c "from backend.database import init_sqlite_database; init_sqlite_database(); print('OK: Database initialized successfully')"

echo.
echo SUCCESS: Environment setup completed!
echo.
echo Run start.bat to launch the system
echo.
pause
