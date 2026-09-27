# 🚨 BACKEND STARTUP INSTRUCTIONS

## Current Issue
The backend server starts but then stops immediately when run in background. You need to run it in a dedicated terminal window that stays open.

## ✅ CORRECT WAY TO START BACKEND

### Option 1: Using Batch File (RECOMMENDED)
1. Open a **NEW Command Prompt or PowerShell window**
2. Navigate to backend directory:
   ```cmd
   cd G:\Samples\IRIS-Showcase\smart-logistics-system-main\backend
   ```
3. Run the batch file:
   ```cmd
   start-backend.bat
   ```
4. **IMPORTANT: Keep this window OPEN!** Do NOT close it.
5. You should see:
   ```
   SERVER STARTING ON http://0.0.0.0:5000
   Server is ready! Press Ctrl+C to stop.
   ```

### Option 2: Manual Start
1. Open a **NEW terminal window**
2. Navigate and activate:
   ```cmd
   cd G:\Samples\IRIS-Showcase\smart-logistics-system-main\backend
   .venv\Scripts\activate
   ```
3. Run the server:
   ```cmd
   python run_server.py
   ```
4. **Keep this window OPEN!**

## ✅ VERIFY SERVER IS RUNNING

### Test 1: Check Process
In a **different** terminal window, run:
```powershell
Get-Process python -ErrorAction SilentlyContinue
```
You should see at least one Python process.

### Test 2: Check Port
```powershell
netstat -ano | findstr ":5000"
```
You should see something like:
```
TCP    0.0.0.0:5000    0.0.0.0:0    LISTENING    12345
```

### Test 3: Test Health Endpoint
```powershell
Invoke-RestMethod -Uri "http://localhost:5000/api/health"
```
Expected response:
```json
{
  "status": "healthy",
  "timestamp": "2026-02-13T..."
}
```

### Test 4: Test Agent Endpoints
```powershell
# Traditional agents
Invoke-RestMethod -Uri "http://localhost:5000/api/agents/status"

# GenAI agents
Invoke-RestMethod -Uri "http://localhost:5000/api/genai-agents/status"

# Comparison endpoint
Invoke-RestMethod -Uri "http://localhost:5000/api/genai-agents/compare"
```

## 🐛 TROUBLESHOOTING

### "Traditional agents not available"
This means the frontend cannot reach `http://localhost:5000/api/agents/status`

**Check:**
1. Is the backend terminal window still open?
2. Run: `netstat -ano | findstr ":5000"` - is port 5000 listening?
3. Test manually: `Invoke-RestMethod -Uri "http://localhost:5000/api/agents/status"`
4. Check backend terminal for errors

### "GenAI agents not available"
This means either:
- Backend is not running, OR
- Azure OpenAI credentials are not configured

**Check:**
1. First verify backend is running (see above)
2. Check `.env` file has:
   ```env
   AZURE_OPENAI_API_KEY=your_key
   AZURE_OPENAI_ENDPOINT=your_endpoint
   AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4.1
   ENABLE_GENAI_AGENTS=true
   ```
3. Test GenAI endpoint: `Invoke-RestMethod -Uri "http://localhost:5000/api/genai-agents/health"`

### Backend Window Closes Immediately
If the backend window closes right after opening:
1. Check for Python syntax errors
2. Run manually in terminal to see error:
   ```cmd
   cd backend
   .venv\Scripts\activate
   python run_server.py
   ```
3. Look for import errors or missing dependencies

### Port 5000 Already in Use
If you get "Address already in use" error:
1. Find the process:
   ```powershell
   Get-NetTCPConnection -LocalPort 5000 | Select-Object OwningProcess
   ```
2. Kill it:
   ```powershell
   Stop-Process -Id <ProcessId> -Force
   ```
3. Start backend again

### Frontend Shows "Network Error"
1. Check backend is running
2. Check CORS is enabled (it is in app.py)
3. Make sure frontend is calling `http://localhost:5000` not `http://localhost:5173`
4. Check browser console for actual error

## 📝 COMPLETE STARTUP CHECKLIST

- [ ] Terminal 1: Backend started with `start-backend.bat`
- [ ] Backend terminal shows "Server is ready!"
- [ ] Keep backend terminal OPEN (don't close it!)
- [ ] Verified: `netstat -ano | findstr ":5000"` shows LISTENING
- [ ] Verified: `Invoke-RestMethod http://localhost:5000/api/health` works
- [ ] Terminal 2: Frontend started with `npm run dev`
- [ ] Frontend running on http://localhost:5173
- [ ] Open browser to http://localhost:5173
- [ ] Navigate to AI Agents > Agent Comparison
- [ ] Should see: "Traditional agents: Available"
- [ ] Should see: "GenAI agents: Available" (if Azure configured)

## 🎯 QUICK TEST SCRIPT

Run this in PowerShell to test all endpoints:

```powershell
# Test script
$baseUrl = "http://localhost:5000"

Write-Host "Testing Backend Endpoints..." -ForegroundColor Cyan

# Test 1: Health
try {
    $r = Invoke-RestMethod "$baseUrl/api/health"
    Write-Host "[OK] Health endpoint" -ForegroundColor Green
} catch {
    Write-Host "[FAIL] Health endpoint: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 2: Traditional agents
try {
    $r = Invoke-RestMethod "$baseUrl/api/agents/status"
    Write-Host "[OK] Traditional agents" -ForegroundColor Green
} catch {
    Write-Host "[FAIL] Traditional agents: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 3: GenAI agents
try {
    $r = Invoke-RestMethod "$baseUrl/api/genai-agents/status"
    Write-Host "[OK] GenAI agents" -ForegroundColor Green
} catch {
    Write-Host "[FAIL] GenAI agents: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 4: Comparison
try {
    $r = Invoke-RestMethod "$baseUrl/api/genai-agents/compare"
    Write-Host "[OK] Comparison endpoint" -ForegroundColor Green
} catch {
    Write-Host "[FAIL] Comparison: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "`nIf all tests passed, backend is working correctly!" -ForegroundColor Green
```

Save this as `test_backend.ps1` and run it after starting the backend.

## 🎉 SUCCESS INDICATORS

When everything is working correctly:

**Backend Terminal Shows:**
```
================================================================================
SERVER STARTING ON http://0.0.0.0:5000
================================================================================

Server is ready! Press Ctrl+C to stop.

INFO:werkzeug: * Running on all addresses (0.0.0.0)
INFO:werkzeug: * Running on http://127.0.0.1:5000
```

**Frontend Shows:**
```
✅ Traditional Agents: Available
   - Route Optimizer: Ready
   - Demand Predictor: Ready

✅ GenAI Agents: Available
   - Route Optimizer: Ready
   - Demand Predictor: Ready
```

**Browser Network Tab Shows:**
```
200 GET http://localhost:5000/api/agents/status
200 GET http://localhost:5000/api/genai-agents/status
200 GET http://localhost:5000/api/genai-agents/compare
```

## 🆘 STILL NOT WORKING?

If you've followed all steps and it still doesn't work:

1. **Restart everything:**
   - Close all terminal windows
   - Stop all Python processes: `Get-Process python | Stop-Process -Force`
   - Wait 5 seconds
   - Start backend in new terminal
   - Wait until you see "Server is ready!"
   - Start frontend in another terminal
   - Test endpoints

2. **Check the logs:**
   - Backend: Look at the backend terminal output
   - Frontend: Open browser DevTools > Console
   - Check for specific error messages

3. **Manual verification:**
   ```powershell
   cd backend
   python test_flask_app.py
   ```
   This tests the Flask app without running the server.

4. **Environment issues:**
   - Verify virtual environment is activated: `.venv\Scripts\activate`
   - Verify dependencies: `pip list | findstr flask`
   - Reinstall if needed: `pip install -r requirements.txt`

Remember: The backend MUST be running in a terminal window that stays open!

