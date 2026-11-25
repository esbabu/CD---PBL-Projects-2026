@echo off
title Secure OTA Compiler Web Demo
echo ==========================================================
echo  Starting Secure OTA Compiler Web Demo...
echo ==========================================================
echo Server URL: http://localhost:5050
echo Press Ctrl+C in this terminal window to stop the server.
echo.

:: Open default browser after 2 seconds once Flask server initializes
start "" powershell -NoProfile -Command "Start-Sleep -Seconds 2; Start-Process 'http://localhost:5050'"

:: Launch Flask server in WSL dynamically relative to this batch file's location
wsl -e bash -c "cd \"$(wslpath -a '%~dp0')\" && if [ -f .venv/bin/python3 ]; then .venv/bin/python3 web-demo/app.py; else python3 web-demo/app.py; fi"

pause
