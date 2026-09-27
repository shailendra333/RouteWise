# Complete Frontend Reorganization
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  COMPLETING FRONTEND REORGANIZATION" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

$rootPath = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $rootPath

Write-Host "Step 1: Moving remaining files to frontend..." -ForegroundColor Yellow

if (Test-Path "src") {
    Write-Host "  - Moving src folder..." -ForegroundColor Gray
    Move-Item -Path "src" -Destination "frontend\" -Force
    Write-Host "  - ✓ src moved successfully" -ForegroundColor Green
} else {
    Write-Host "  - src already in frontend" -ForegroundColor Gray
}

if (Test-Path "public") {
    Write-Host "  - Moving public folder..." -ForegroundColor Gray
    Move-Item -Path "public" -Destination "frontend\" -Force
}

if (Test-Path "dist") {
    Write-Host "  - Moving dist folder..." -ForegroundColor Gray
    if (Test-Path "frontend\dist") {
        Remove-Item -Recurse -Force "frontend\dist"
    }
    Move-Item -Path "dist" -Destination "frontend\" -Force
}

Write-Host ""
Write-Host "Step 2: Verifying frontend structure..." -ForegroundColor Yellow
$errors = @()

if (Test-Path "frontend\src") {
    Write-Host "  ✓ frontend\src exists" -ForegroundColor Green
} else {
    Write-Host "  ✗ ERROR: frontend\src is missing!" -ForegroundColor Red
    $errors += "src"
}

if (Test-Path "frontend\index.html") {
    Write-Host "  ✓ frontend\index.html exists" -ForegroundColor Green
} else {
    Write-Host "  ✗ ERROR: frontend\index.html is missing!" -ForegroundColor Red
    $errors += "index.html"
}

if (Test-Path "frontend\package.json") {
    Write-Host "  ✓ frontend\package.json exists" -ForegroundColor Green
} else {
    Write-Host "  ✗ ERROR: frontend\package.json is missing!" -ForegroundColor Red
    $errors += "package.json"
}

if ($errors.Count -gt 0) {
    Write-Host ""
    Write-Host "Errors found. Cannot continue." -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""
Write-Host "Step 3: Cleaning frontend cache..." -ForegroundColor Yellow
Set-Location "frontend"

if (Test-Path ".vite") {
    Remove-Item -Recurse -Force ".vite"
    Write-Host "  - Removed .vite cache" -ForegroundColor Green
}

if (Test-Path "node_modules\.vite") {
    Remove-Item -Recurse -Force "node_modules\.vite"
    Write-Host "  - Removed node_modules\.vite cache" -ForegroundColor Green
}

Write-Host ""
Write-Host "Step 4: Reinstalling frontend dependencies..." -ForegroundColor Yellow
npm install

Set-Location $rootPath

Write-Host ""
Write-Host "============================================" -ForegroundColor Green
Write-Host "  REORGANIZATION COMPLETE!" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Green
Write-Host ""
Write-Host "New structure:" -ForegroundColor Cyan
Write-Host "  frontend\src\         - React source code" -ForegroundColor White
Write-Host "  frontend\index.html   - HTML template" -ForegroundColor White
Write-Host "  frontend\package.json - Dependencies" -ForegroundColor White
Write-Host "  backend\              - Flask backend" -ForegroundColor White
Write-Host ""
Write-Host "To start the application:" -ForegroundColor Yellow
Write-Host "  Terminal 1: cd backend && python app.py" -ForegroundColor White
Write-Host "  Terminal 2: cd frontend && npm run dev" -ForegroundColor White
Write-Host ""
Read-Host "Press Enter to exit"

