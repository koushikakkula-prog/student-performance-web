@echo off
title Student Performance Prediction System
echo ===================================================
echo   Starting Student Performance Prediction System...
echo ===================================================
echo.
cd /d "%~dp0"

echo Opening browser at http://127.0.0.1:5000 ...
start http://127.0.0.1:5000

echo.
echo Running Python Flask Server (Press Ctrl+C to stop)...
python app.py
pause
