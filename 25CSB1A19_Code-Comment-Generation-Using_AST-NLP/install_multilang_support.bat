@echo off
setlocal
cd /d "%~dp0"
echo Installing structural parser support for C, C++, Java, JavaScript and TypeScript...
py -m pip install -r requirements-multilang.txt
if errorlevel 1 (
  echo.
  echo Installation failed. Check Python and internet connectivity, then retry.
  pause
  exit /b 1
)
echo.
echo Multi-language parser package installed.
echo Tree-sitter grammars are downloaded on first use if they are not already cached.
pause
