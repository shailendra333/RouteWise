@echo off
echo ====================================
echo Restarting Frontend with Clean Cache
echo ====================================
echo.

cd /d "%~dp0"

echo Stopping any running dev servers...
taskkill /F /IM node.exe 2>nul

echo.
echo Clearing Vite cache...
if exist "node_modules\.vite" (
    rmdir /s /q "node_modules\.vite"
    echo Vite cache cleared
) else (
    echo No Vite cache found
)

echo.
echo Starting frontend dev server...
echo.
echo Frontend will be available at http://localhost:5173
echo All API calls will now go to http://localhost:8000
echo.

npm run dev

