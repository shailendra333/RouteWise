@echo off
echo ====================================
echo Starting Smart Logistics Backend
echo ====================================
echo.

cd /d "%~dp0"

echo Activating virtual environment...
call .venv\Scripts\activate.bat
if errorlevel 1 (
    echo ERROR: Failed to activate virtual environment
    echo Make sure .venv exists in the backend directory
    pause
    exit /b 1
)

echo.
echo Starting Flask application on http://localhost:5000
echo Press Ctrl+C to stop the server
echo.

python run_server.py
if errorlevel 1 (
    echo.
    echo ERROR: Server failed to start
    pause
)
