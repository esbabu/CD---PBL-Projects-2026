@echo off
setlocal
cd /d "%~dp0"

if not exist "venv\Scripts\python.exe" (
    echo [ERROR] Virtual environment not found. Run setup.bat or create it with: python -m venv venv
    exit /b 1
)

set "PYTHONPATH=%CD%\src;%PYTHONPATH%"

if "%~1"=="" (
    venv\Scripts\python.exe src\pipeline.py test_files\test_02_cwe190_overflow.c --no-carbon --model results\pyg_gnn_v9\best_pyg_model.pt
) else (
    venv\Scripts\python.exe src\pipeline.py %* --no-carbon --model results\pyg_gnn_v9\best_pyg_model.pt
)
