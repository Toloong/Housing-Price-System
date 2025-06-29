@echo off
setlocal EnableDelayedExpansion
chcp 65001 >nul
title Housing Price Analysis System - Windows Installer

:: Clear screen and show header
cls
echo.
echo ================================================
echo    Housing Price Analysis System v3.0
echo    Windows One-Click Installer
echo ================================================
echo.
echo.    ####    ####   #    #  ####  # #    #  ####
echo.    #   #  #    #  #    #  #     # ##   # #    
echo.    ####   #    #  #    #  ####  # # #  # #  ##
echo.    #   #  #    #  #    #     #  # #  # # #   #
echo.    #   #   ####    ####   ####  # #   ##  ####
echo.
echo.    ####   ####   #  ####  ####
echo.    #   #  #   #  #  #     #   
echo.    ####   ####   #  #     #### 
echo.    #      #   #  #  #     #   #
echo.    #      #   #  #  ####  ####
echo.
echo ================================================
echo.

:: Check if running in correct directory
if not exist "requirements.txt" (
    echo ERROR: Please run this script from the project root directory
    echo        Current directory should contain requirements.txt file
    echo.
    pause
    exit /b 1
)

echo Welcome to Housing Price Analysis System!
echo.
echo This installer will automatically:
echo   * Check and install Python dependencies
echo   * Create virtual environment
echo   * Configure database (optional)
echo   * Launch application system
echo.

set /p confirm="Continue with installation? (Y/N): "
if /i not "%confirm%"=="Y" (
    echo Installation cancelled by user
    pause
    exit /b 0
)

echo.
echo ====================================================
echo                Starting Installation
echo ====================================================
echo.

:: Check Python installation
echo Checking Python environment...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python not installed
    echo.
    echo Please install Python first:
    echo    1. Visit https://python.org
    echo    2. Download Python 3.8 or higher
    echo    3. Check "Add to PATH" during installation
    echo    4. Restart this script
    echo.
    pause
    exit /b 1
)

for /f "tokens=2" %%a in ('python --version 2^>^&1') do set python_version=%%a
echo SUCCESS: Python installed: %python_version%

:: Create virtual environment
echo.
echo Setting up virtual environment...
if exist ".venv" (
    echo SUCCESS: Virtual environment already exists
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

:: Activate virtual environment
echo Activating virtual environment...
call .venv\Scripts\activate.bat
if %errorlevel% neq 0 (
    echo ERROR: Failed to activate virtual environment
    pause
    exit /b 1
)
echo SUCCESS: Virtual environment activated

:: Install dependencies
echo.
echo Installing project dependencies...
echo    This may take a few minutes, please wait...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ERROR: Failed to install dependencies
    echo.
    echo Possible solutions:
    echo    1. Check internet connection
    echo    2. Upgrade pip: python -m pip install --upgrade pip
    echo    3. Use mirror: pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
    echo.
    pause
    exit /b 1
)
echo SUCCESS: Dependencies installed successfully

:: Database configuration choice
echo.
echo ====================================================
echo                Database Configuration
echo ====================================================
echo.
echo User management features require PostgreSQL database support
echo.
echo Choose an option:
echo   1. Configure PostgreSQL (Recommended, full features)
echo   2. Skip database configuration (Basic features only)
echo.

set /p db_choice="Please choose (1-2): "

if "%db_choice%"=="1" (
    echo.
    echo Starting PostgreSQL configuration...
    
    :: Check if PostgreSQL is installed
    psql --version >nul 2>&1
    if %errorlevel% neq 0 (
        echo WARNING: PostgreSQL not detected
        echo.
        echo Please install PostgreSQL:
        echo    1. Visit https://www.postgresql.org/download/windows/
        echo    2. Download and install PostgreSQL 12+
        echo    3. Remember the postgres user password
        echo    4. Re-run this script
        echo.
        set /p skip_db="Skip database configuration and continue? (Y/N): "
        if /i "!skip_db!"=="Y" (
            echo Skipping database configuration
        ) else (
            pause
            exit /b 1
        )
    ) else (
        echo SUCCESS: PostgreSQL installed
        echo Running database configuration script...
        
        if exist "setup_postgresql.ps1" (
            powershell -ExecutionPolicy Bypass -Command "& {Set-ExecutionPolicy Bypass -Scope Process; .\setup_postgresql.ps1}"
        ) else (
            echo Manual database configuration...
            python init_database.py
        )
    )
) else (
    echo Skipping database configuration, basic features only
)

:: Installation complete
echo.
echo ====================================================
echo                Installation Complete!
echo ====================================================
echo.
echo SUCCESS: Housing Price Analysis System installed successfully!
echo.
echo Features:
echo    * House price search and query
echo    * Trend analysis and visualization
echo    * City comparison analysis
echo    * AI intelligent assistant
if "%db_choice%"=="1" (
    echo    * User management system (configured)
) else (
    echo    * User management system (not configured)
)
echo.
echo Start system now?
set /p start_now="Launch application immediately (Y/N): "

if /i "%start_now%"=="Y" (
    echo.
    echo Starting system...
    call start_system.bat
) else (
    echo.
    echo Manual startup instructions:
    echo    1. Double-click start_system.bat
    echo    2. Or run .\start_system.ps1
    echo.
    echo Access URLs:
    echo    Frontend: http://localhost:8501
    echo    Backend API: http://localhost:8000
    echo.
    echo For more help, see WINDOWS_GUIDE.md
)

echo.
echo Thank you for using Housing Price Analysis System!
pause
