@echo off
echo ============================================
echo   FIXING VITE LOADING ISSUE
echo ============================================
echo.

cd /d "%~dp0"

echo Step 1: Clearing Vite cache...
if exist .vite (
    rmdir /s /q .vite
    echo   - Cleared .vite directory
)

if exist node_modules\.vite (
    rmdir /s /q node_modules\.vite
    echo   - Cleared node_modules\.vite directory
)

echo.
echo Step 2: Reinstalling dependencies...
call npm install

echo.
echo ============================================
echo   FIX COMPLETE!
echo ============================================
echo.
echo Now you can run: npm run dev
echo.
pause

