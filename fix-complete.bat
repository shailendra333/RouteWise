@echo off
echo ============================================
echo   FIXING VITE SERVER ISSUES
echo ============================================
echo.

cd /d "%~dp0"

echo Step 1: Stopping any running processes...
echo   (If dev server is running, press Ctrl+C to stop it first)
timeout /t 3 >nul

echo.
echo Step 2: Cleaning all cache and build artifacts...

if exist .vite (
    echo   - Removing .vite cache...
    rmdir /s /q .vite
)

if exist node_modules\.vite (
    echo   - Removing node_modules\.vite cache...
    rmdir /s /q node_modules\.vite
)

if exist dist (
    echo   - Removing dist folder...
    rmdir /s /q dist
)

echo.
echo Step 3: Cleaning node_modules...
if exist node_modules (
    echo   - Removing node_modules...
    rmdir /s /q node_modules
)

if exist package-lock.json (
    echo   - Removing package-lock.json...
    del /f /q package-lock.json
)

echo.
echo Step 4: Clearing npm cache...
call npm cache clean --force

echo.
echo Step 5: Reinstalling dependencies...
call npm install

echo.
echo Step 6: Verifying installation...
if exist node_modules (
    echo   ✓ node_modules installed successfully
) else (
    echo   ✗ Installation failed - please check npm errors above
    pause
    exit /b 1
)

echo.
echo ============================================
echo   FIX COMPLETE!
echo ============================================
echo.
echo Now you can start the dev server:
echo   npm run dev
echo.
echo If issues persist, try:
echo   npm run dev -- --force
echo.
pause

