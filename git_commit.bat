@echo off
chcp 65001 >nul
echo Git Commit Script
echo ================
echo.

echo [1/5] Checking Git status...
git status

echo.
echo [2/5] Adding all files to staging area...
git add .
git add -A

echo.
echo [3/5] Showing files to be committed...
git status --short

echo.
echo [4/5] Committing changes...
set /p commit_message="Enter commit message (Press Enter for default): "
if "%commit_message%"=="" set "commit_message=feat: Complete housing price analysis system refactoring - SQLite database, simplified project structure"

git commit -m "%commit_message%"
if %errorlevel% neq 0 (
    echo Failed to commit
    pause
    exit /b 1
)

echo Local commit successful

echo.
echo [5/5] Pushing to remote repository...
echo Make sure remote repository is set up (git remote add origin <repo-url>)
set /p push_confirm="Push to remote repository? (y/N): "
if /i "%push_confirm%"=="y" (
    echo Checking current branch...
    for /f "tokens=*" %%i in ('git branch --show-current') do set current_branch=%%i
    echo Current branch: %current_branch%
    
    git push origin %current_branch%
    if %errorlevel% neq 0 (
        echo Push failed, trying to push to main branch...
        git push origin HEAD:main
        if %errorlevel% neq 0 (
            echo Push failed, please check remote repository settings
            echo Manual push commands:
            echo   git push origin %current_branch%
            echo   git push origin HEAD:main
            pause
            exit /b 1
        )
    )
    echo Push successful!
) else (
    echo Skipping push, you can manually push later:
    for /f "tokens=*" %%i in ('git branch --show-current') do set current_branch=%%i
    echo   git push origin %current_branch%
)

echo.
echo Git operations completed!
pause
