@echo off
echo ============================================
echo   COMPLETING FRONTEND REORGANIZATION
echo ============================================
echo.

cd /d "%~dp0"

echo Step 1: Moving remaining files to frontend...

if exist src (
    echo   - Moving src folder...
    move src frontend\
    if errorlevel 1 (
        echo   ERROR: Failed to move src folder
        pause
        exit /b 1
    )
    echo   - ✓ src moved successfully
) else (
    echo   - src already in frontend
)

if exist public (
    echo   - Moving public folder...
    move public frontend\
)

if exist dist (
    echo   - Moving dist folder...
    if exist frontend\dist (
        rmdir /s /q frontend\dist
    )
    move dist frontend\
)

echo.
echo Step 2: Verifying frontend structure...
if exist frontend\src (
    echo   ✓ frontend\src exists
) else (
    echo   ✗ ERROR: frontend\src is missing!
    pause
    exit /b 1
)

if exist frontend\index.html (
    echo   ✓ frontend\index.html exists
) else (
    echo   ✗ ERROR: frontend\index.html is missing!
    pause
    exit /b 1
)

if exist frontend\package.json (
    echo   ✓ frontend\package.json exists
) else (
    echo   ✗ ERROR: frontend\package.json is missing!
    pause
    exit /b 1
)

echo.
echo Step 3: Cleaning frontend cache...
cd frontend

if exist .vite (
    rmdir /s /q .vite
    echo   - Removed .vite cache
)

if exist node_modules\.vite (
    rmdir /s /q node_modules\.vite
    echo   - Removed node_modules\.vite cache
)

echo.
echo Step 4: Reinstalling frontend dependencies...
call npm install

echo.
echo ============================================
echo   REORGANIZATION COMPLETE!
echo ============================================
echo.
echo New structure:
echo   frontend\src\         - React source code
echo   frontend\index.html   - HTML template
echo   frontend\package.json - Dependencies
echo   backend\              - Flask backend
echo.
echo To start the application:
echo   Terminal 1: cd backend ^&^& python app.py
echo   Terminal 2: cd frontend ^&^& npm run dev
echo.
pause

