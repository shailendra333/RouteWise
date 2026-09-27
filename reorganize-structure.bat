@echo off
echo ============================================
echo   REORGANIZING PROJECT STRUCTURE
echo ============================================
echo.

cd /d "%~dp0"

echo Step 1: Creating frontend directory...
if not exist frontend mkdir frontend
echo   - Created frontend directory

echo.
echo Step 2: Moving frontend files...

if exist src (
    echo   - Moving src...
    move src frontend\
)

if exist public (
    echo   - Moving public...
    move public frontend\
)

if exist index.html (
    echo   - Moving index.html...
    move index.html frontend\
)

if exist package.json (
    echo   - Moving package.json...
    move package.json frontend\
)

if exist package-lock.json (
    echo   - Moving package-lock.json...
    move package-lock.json frontend\
)

if exist tsconfig.json (
    echo   - Moving tsconfig.json...
    move tsconfig.json frontend\
)

if exist tsconfig.app.json (
    echo   - Moving tsconfig.app.json...
    move tsconfig.app.json frontend\
)

if exist tsconfig.node.json (
    echo   - Moving tsconfig.node.json...
    move tsconfig.node.json frontend\
)

if exist vite.config.ts (
    echo   - Moving vite.config.ts...
    move vite.config.ts frontend\
)

if exist eslint.config.js (
    echo   - Moving eslint.config.js...
    move eslint.config.js frontend\
)

if exist postcss.config.js (
    echo   - Moving postcss.config.js...
    move postcss.config.js frontend\
)

if exist tailwind.config.js (
    echo   - Moving tailwind.config.js...
    move tailwind.config.js frontend\
)

if exist node_modules (
    echo   - Moving node_modules...
    move node_modules frontend\
)

if exist .vite (
    echo   - Moving .vite...
    move .vite frontend\
)

if exist dist (
    echo   - Moving dist...
    move dist frontend\
)

echo.
echo Step 3: Moving fix scripts...

if exist fix-vite-issue.bat (
    move fix-vite-issue.bat frontend\
)

if exist fix-vite-issue.ps1 (
    move fix-vite-issue.ps1 frontend\
)

if exist FIX_README.md (
    move FIX_README.md frontend\
)

if exist VITE_LOADING_FIX.md (
    move VITE_LOADING_FIX.md frontend\
)

echo.
echo ============================================
echo   REORGANIZATION COMPLETE!
echo ============================================
echo.
echo New structure:
echo   backend/     - Python Flask backend
echo   frontend/    - React TypeScript frontend
echo   docs/        - Documentation
echo.
echo To start the project now:
echo   Backend:  cd backend ^&^& python app.py
echo   Frontend: cd frontend ^&^& npm run dev
echo.
pause

