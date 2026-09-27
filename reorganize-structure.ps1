# Reorganize Project Structure - Move Frontend to Separate Folder
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  REORGANIZING PROJECT STRUCTURE" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

$rootPath = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $rootPath

# Create frontend directory
Write-Host "Step 1: Creating frontend directory..." -ForegroundColor Yellow
if (-not (Test-Path "frontend")) {
    New-Item -ItemType Directory -Path "frontend" | Out-Null
    Write-Host "  - Created frontend directory" -ForegroundColor Green
}

# List of frontend files/folders to move
$itemsToMove = @(
    "src",
    "public",
    "index.html",
    "package.json",
    "package-lock.json",
    "tsconfig.json",
    "tsconfig.app.json",
    "tsconfig.node.json",
    "vite.config.ts",
    "eslint.config.js",
    "postcss.config.js",
    "tailwind.config.js",
    "node_modules",
    ".vite",
    "dist"
)

Write-Host ""
Write-Host "Step 2: Moving frontend files..." -ForegroundColor Yellow

foreach ($item in $itemsToMove) {
    if (Test-Path $item) {
        Write-Host "  - Moving $item..." -ForegroundColor Gray
        Move-Item -Path $item -Destination "frontend\" -Force
    }
}

# Move fix scripts to frontend
$fixScripts = @(
    "fix-vite-issue.bat",
    "fix-vite-issue.ps1",
    "FIX_README.md",
    "VITE_LOADING_FIX.md"
)

Write-Host ""
Write-Host "Step 3: Moving fix scripts to frontend..." -ForegroundColor Yellow
foreach ($script in $fixScripts) {
    if (Test-Path $script) {
        Move-Item -Path $script -Destination "frontend\" -Force
        Write-Host "  - Moved $script" -ForegroundColor Gray
    }
}

Write-Host ""
Write-Host "============================================" -ForegroundColor Green
Write-Host "  REORGANIZATION COMPLETE!" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Green
Write-Host ""
Write-Host "New structure:" -ForegroundColor Cyan
Write-Host "  backend/     - Python Flask backend" -ForegroundColor White
Write-Host "  frontend/    - React TypeScript frontend" -ForegroundColor White
Write-Host "  docs/        - Documentation" -ForegroundColor White
Write-Host ""
Write-Host "To start the project now:" -ForegroundColor Yellow
Write-Host "  Backend:  cd backend && python app.py" -ForegroundColor White
Write-Host "  Frontend: cd frontend && npm run dev" -ForegroundColor White
Write-Host ""
Read-Host "Press Enter to exit"

