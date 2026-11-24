# tools/build_extension.ps1
# Automates compiling and packaging the Compiler Error Explainer VS Code Extension

$ErrorActionPreference = "Stop"
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$extDir = Join-Path (Split-Path -Parent $scriptDir) "vscode-extension"

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "Building Compiler Error Explainer VS Code Extension..." -ForegroundColor Cyan
Write-Host "Directory: $extDir" -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan

Set-Location $extDir

Write-Host "`n[1/3] Installing Node.js dependencies..." -ForegroundColor Yellow
npm install

Write-Host "`n[2/3] Compiling TypeScript to JavaScript..." -ForegroundColor Yellow
npm run compile

Write-Host "`n[3/3] Running Extension Unit Tests..." -ForegroundColor Yellow
npm test

Write-Host "`n[4/4] Packaging extension into VSIX installer..." -ForegroundColor Yellow
try {
    npx @vscode/vsce package --no-dependencies
    Write-Host "`nExtension successfully built and packaged into .vsix!" -ForegroundColor Green
    Write-Host "To install in VS Code, run:" -ForegroundColor Green
    Write-Host "  code --install-extension vscode-extension/compiler-error-explainer-0.1.0.vsix" -ForegroundColor White
} catch {
    Write-Host "`nVSIX packaging skipped or requires @vscode/vsce. Compiled JS outputs are ready in out/." -ForegroundColor Yellow
}
