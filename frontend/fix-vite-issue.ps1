# Fix Vite Loading Issue
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  FIXING VITE LOADING ISSUE" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

$rootPath = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $rootPath

Write-Host "Step 1: Clearing Vite cache..." -ForegroundColor Yellow
if (Test-Path ".vite") {
    Remove-Item -Recurse -Force ".vite"
    Write-Host "  - Cleared .vite directory" -ForegroundColor Green
}

if (Test-Path "node_modules\.vite") {
    Remove-Item -Recurse -Force "node_modules\.vite"
    Write-Host "  - Cleared node_modules\.vite directory" -ForegroundColor Green
}

Write-Host ""
Write-Host "Step 2: Reinstalling dependencies..." -ForegroundColor Yellow
npm install

Write-Host ""
Write-Host "============================================" -ForegroundColor Green
Write-Host "  FIX COMPLETE!" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Green
Write-Host ""
Write-Host "Now you can run: npm run dev" -ForegroundColor Cyan
Write-Host ""
Read-Host "Press Enter to exit"

