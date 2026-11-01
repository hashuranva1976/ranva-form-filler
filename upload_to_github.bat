@echo off
chcp 65001 >nul
title GitHub Upload Helper
cd /d "%~dp0"

echo ==============================================================
echo       AI Form Auto-Filler - GitHub Auto Upload Tool
echo ==============================================================
echo.
echo GitHub par repository banavya pachhi tene link ahi paste karo:
echo (Example: https://github.com/your-username/form-filler.git)
echo.
set /p REPO_URL="GitHub Repository URL: "

if "%REPO_URL%"=="" (
    echo.
    echo Bhul: URL khali che. Farithi prayas karo.
    pause
    exit /b
)

echo.
echo 1. Initializing Git...
git init
git branch -M main

echo 2. Adding files...
git add .

echo 3. Creating commit...
git commit -m "Deploy AI Form Auto-Filler to Cloud"

echo 4. Setting remote repository...
git remote remove origin 2>nul
git remote add origin %REPO_URL%

echo 5. Pushing files to GitHub...
git push -u origin main

echo.
echo ==============================================================
echo Tamari files safaltapurvak GitHub par upload thai gai che!
echo Have Render.com par jaine 'Connect' kari do.
echo ==============================================================
pause
