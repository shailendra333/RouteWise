# Complete Vite Server Fix
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  FIXING VITE SERVER ISSUES" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

$rootPath = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $rootPath

Write-Host "Step 1: Stopping any running processes..." -ForegroundColor Yellow
Write-Host "  (If dev server is running, press Ctrl+C to stop it first)" -ForegroundColor Gray
Start-Sleep -Seconds 2

Write-Host ""
Write-Host "Step 2: Cleaning all cache and build artifacts..." -ForegroundColor Yellow

if (Test-Path ".vite") {
    Remove-Item -Recurse -Force ".vite"
    Write-Host "  - Removed .vite cache" -ForegroundColor Green
}

if (Test-Path "node_modules\.vite") {
    Remove-Item -Recurse -Force "node_modules\.vite"
    Write-Host "  - Removed node_modules\.vite cache" -ForegroundColor Green
}

if (Test-Path "dist") {
    Remove-Item -Recurse -Force "dist"
    Write-Host "  - Removed dist folder" -ForegroundColor Green
}

Write-Host ""
Write-Host "Step 3: Cleaning node_modules..." -ForegroundColor Yellow
if (Test-Path "node_modules") {
    Remove-Item -Recurse -Force "node_modules"
    Write-Host "  - Removed node_modules" -ForegroundColor Green
}

if (Test-Path "package-lock.json") {
    Remove-Item -Force "package-lock.json"
    Write-Host "  - Removed package-lock.json" -ForegroundColor Green
}

Write-Host ""
Write-Host "Step 4: Clearing npm cache..." -ForegroundColor Yellow
npm cache clean --force

Write-Host ""
Write-Host "Step 5: Reinstalling dependencies..." -ForegroundColor Yellow
npm install

Write-Host ""
Write-Host "Step 6: Verifying installation..." -ForegroundColor Yellow
if (Test-Path "node_modules") {
    Write-Host "  ✓ node_modules installed successfully" -ForegroundColor Green
} else {
    Write-Host "  ✗ Installation failed - please check npm errors above" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""
Write-Host "============================================" -ForegroundColor Green
Write-Host "  FIX COMPLETE!" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Green
Write-Host ""
Write-Host "Now you can start the dev server:" -ForegroundColor Cyan
Write-Host "  npm run dev" -ForegroundColor White
Write-Host ""
Write-Host "If issues persist, try:" -ForegroundColor Yellow
Write-Host "  npm run dev -- --force" -ForegroundColor White
Write-Host ""
Read-Host "Press Enter to exit"

