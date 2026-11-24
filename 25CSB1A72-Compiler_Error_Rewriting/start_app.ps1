$ErrorActionPreference = "Stop"

Set-Location -LiteralPath $PSScriptRoot

$python = Join-Path $PSScriptRoot ".venv\Scripts\python.exe"
$activate = Join-Path $PSScriptRoot ".venv\Scripts\Activate.ps1"
if (-not (Test-Path -LiteralPath $python -PathType Leaf)) {
    Write-Error "The project virtual environment is missing. Create it and install requirements.txt first."
    exit 1
}
if (-not (Test-Path -LiteralPath $activate -PathType Leaf)) {
    Write-Error "The virtual environment activation script is missing: $activate"
    exit 1
}

. $activate

foreach ($tool in @("g++", "gcc", "clang++", "javac", "java", "node", "dot")) {
    if (Get-Command $tool -ErrorAction SilentlyContinue) {
        Write-Host "[found] $tool"
    } else {
        Write-Warning "[optional] $tool not installed; related functionality may be unavailable."
    }
}

Write-Host "Starting the dashboard at http://localhost:5000 (127.0.0.1 only; Flask debug off)."
& $python (Join-Path $PSScriptRoot "src\webapp.py")
exit $LASTEXITCODE
