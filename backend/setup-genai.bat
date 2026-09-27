@echo off
echo ============================================
echo   GenAI AGENTS SETUP
echo ============================================
echo.

cd /d "%~dp0"

echo Step 1: Installing required packages...
pip install openai python-dotenv

echo.
echo Step 2: Creating .env file from template...
if not exist .env (
    copy .env.example .env
    echo   - Created .env file
    echo   - Please edit .env with your Azure OpenAI credentials
) else (
    echo   - .env file already exists
)

echo.
echo ============================================
echo   SETUP COMPLETE!
echo ============================================
echo.
echo Next steps:
echo   1. Edit .env file with your Azure OpenAI credentials
echo   2. Run: python app.py
echo   3. Test: curl http://localhost:5000/api/genai-agents/health
echo.
echo Azure OpenAI Setup:
echo   - Get credentials from Azure Portal
echo   - Navigate to your OpenAI resource
echo   - Go to "Keys and Endpoint"
echo   - Copy API key and endpoint to .env
echo.
pause

