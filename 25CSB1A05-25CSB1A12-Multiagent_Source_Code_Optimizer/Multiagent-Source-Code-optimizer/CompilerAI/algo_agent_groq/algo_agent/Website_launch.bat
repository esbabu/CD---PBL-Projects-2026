
@echo off
title CompilerAI - One Click Launcher

echo.
echo ==========================================
echo          COMPILER AI LAUNCHER
echo ==========================================
echo.

:: Get project directory
cd /d "%~dp0"

:: Start Backend
echo [1/3] Starting Backend Server...
start "CompilerAI Backend" cmd /k "cd /d "%~dp0CompilerAI\backend" && python -m uvicorn app.main:app --host 127.0.0.1 --port 8000"

:: Start Frontend
echo [2/3] Starting Frontend Server...
start "CompilerAI Frontend" cmd /k "cd /d "%~dp0CompilerAI\frontend" && npm run dev"

:: Wait for servers to initialize
echo [3/3] Waiting for servers...
timeout /t 8 /nobreak >nul

:: Open website
echo Opening CompilerAI...
start http://localhost:5173

echo.
echo ==========================================
echo       COMPILER AI LAUNCHED!
echo ==========================================
echo Backend: http://127.0.0.1:8000
echo API Docs: http://127.0.0.1:8000/docs
echo Frontend: http://localhost:5173
echo.
exit
