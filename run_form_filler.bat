@echo off
title AI Smart Form Auto-Filler
cd /d "%~dp0"
echo ==============================================================
echo       AI Universal Online Form Auto-Filler Software
echo ==============================================================
echo.
echo Starting Web Server...
start "" "http://127.0.0.1:5000"
python app.py
pause
