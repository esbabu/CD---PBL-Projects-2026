# Dev startup script for Windows PowerShell
$candidatePythons = @(
    "C:\Users\jaish\anaconda3\python.exe",
    "$env:LOCALAPPDATA\Programs\Python\Python314\python.exe",
    "$env:LOCALAPPDATA\Programs\Python\Python312\python.exe",
    "$env:LOCALAPPDATA\Programs\Python\Python311\python.exe",
    "C:\Python314\python.exe",
    "C:\Python312\python.exe",
    "C:\Python311\python.exe"
)

$pythonExe = $null
foreach ($cand in $candidatePythons) {
    if (Test-Path $cand) {
        $pythonExe = $cand
        break
    }
}
if (-not $pythonExe) {
    $cmd = Get-Command python -ErrorAction SilentlyContinue
    if ($cmd -and $cmd.Source -notmatch "WindowsApps") {
        $pythonExe = $cmd.Source
    } else {
        $pythonExe = "python"
    }
}

Write-Host "Starting CompilerAI Backend on http://127.0.0.1:8000 (Python: $pythonExe)..." -ForegroundColor Cyan
Start-Process -FilePath $pythonExe -ArgumentList "-m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload" -WorkingDirectory "$PSScriptRoot\..\backend"

Write-Host "Starting CompilerAI Frontend on http://localhost:5173..." -ForegroundColor Green
Set-Location "$PSScriptRoot\..\frontend"
npm run dev
