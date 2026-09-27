# 🎯 How to Run the Smart Logistics System with Agent Comparison

## Prerequisites
- Python 3.8+ with virtual environment activated
- Node.js 16+ 
- Azure OpenAI credentials (for GenAI agents)

## 🚀 Quick Start (Two Terminals Required)

### Terminal 1: Backend Server

```bash
# Navigate to backend directory
cd backend

# Start the backend server
start-backend.bat
```

**Or using PowerShell:**
```powershell
cd backend
.\start-backend.ps1
```

**Or manually:**
```bash
cd backend
.\.venv\Scripts\activate
python app.py
```

**Expected Output:**
```
✅ Traditional AI Agents API endpoints registered successfully
✅ GenAI Agents API endpoints registered successfully
 * Running on all addresses (0.0.0.0)
 * Running on http://127.0.0.1:5000
 * Running on http://192.168.x.x:5000
```

**⚠️ IMPORTANT: Keep this terminal running!**

### Terminal 2: Frontend Server

Open a **NEW terminal window** and run:

```bash
# Navigate to frontend directory
cd frontend

# Start the frontend dev server
npm run dev
```

**Expected Output:**
```
  VITE v5.x.x  ready in xxx ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: http://192.168.x.x:5173/
```

## 🧪 Verify Everything Works

### Option 1: Use Test Script

In the backend directory (with backend running):
```bash
cd backend
python test_agent_endpoints.py
```

This will test all agent comparison endpoints.

### Option 2: Manual Testing

Test each endpoint with curl or browser:

1. **Backend Health:**
   ```bash
   curl http://localhost:5000/api/health
   ```

2. **Traditional Agents:**
   ```bash
   curl http://localhost:5000/api/agents/status
   ```

3. **GenAI Agents:**
   ```bash
   curl http://localhost:5000/api/genai-agents/status
   ```

4. **Comparison Endpoint (the one that was 404):**
   ```bash
   curl http://localhost:5000/api/genai-agents/compare
   ```

## 🎨 Access the Application

1. Open browser: **http://localhost:5173**
2. Navigate to: **AI Agents** → **Agent Comparison**
3. You should see:
   - ✅ Traditional agents available
   - ✅ GenAI agents available (if Azure OpenAI configured)
   - Full comparison dashboard

## 📋 What Was Fixed

### The Problem
- Error: `404 for /api/genai-agents/compare`
- Message: "Traditional agents not available. Make sure backend is running."
- Message: "GenAI agents not available. Configure Azure OpenAI credentials."

### Root Causes Found
1. **Import Error in `ai_agents/__init__.py`**
   - File was importing non-existent modules (`customer_service_agent`, `fleet_manager_agent`)
   - This prevented the entire `ai_agents` package from loading
   - **FIXED:** Removed non-existent imports

2. **Backend Not Running**
   - The Flask backend server was not started
   - Frontend could not connect to API endpoints
   - **FIXED:** Created startup scripts and documentation

### Files Modified
- ✅ `backend/ai_agents/__init__.py` - Removed invalid imports
- ✅ Created `backend/start-backend.bat` - Easy startup script (Windows)
- ✅ Created `backend/start-backend.ps1` - PowerShell startup script
- ✅ Created `backend/test_agent_endpoints.py` - Endpoint verification script
- ✅ Created `backend/test_routes.py` - Route registration checker
- ✅ Created `AGENT_COMPARISON_FIX.md` - Comprehensive fix documentation

## 🔧 Configuration

### Backend Configuration (`.env`)

Make sure your `backend/.env` file contains:

```env
# Azure OpenAI Configuration
AZURE_OPENAI_API_KEY=your_key_here
AZURE_OPENAI_ENDPOINT=https://your-endpoint.openai.azure.com
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4.1
AZURE_OPENAI_API_VERSION=2025-01-01-preview

# Database
DATABASE_URL=sqlite:///smart_logistics.db

# Flask
FLASK_ENV=development
SECRET_KEY=your_secret_key_here

# Agents
ENABLE_GENAI_AGENTS=true
ENABLE_TRADITIONAL_AGENTS=true

# Logging
LOG_LEVEL=INFO
```

## 🎭 Using the Agent Comparison Dashboard

### Overview Tab
- Compare traditional vs GenAI agent capabilities
- See comparison matrix
- View strengths and weaknesses

### Traditional Agents Tab
- Rule-based agents
- Fast execution (<100ms)
- Genetic Algorithm + OR-Tools for routing
- LSTM for demand forecasting
- Technical explanations

### GenAI Agents Tab
- Azure OpenAI GPT-4 powered
- Natural language explanations
- Context-aware reasoning
- Conversational interface
- Executive report generation

### Side-by-Side Tab
Execute the same task on both systems and compare:
- **Execution time:** Traditional (fast) vs GenAI (1-3s)
- **Decision quality:** Algorithm vs AI reasoning
- **Explanation style:** Technical vs Natural language
- **Adaptability:** Fixed rules vs Context-aware

## 🧪 Testing Agents

### Test Route Optimization
1. Go to Side-by-Side tab
2. Click "Execute Route Optimizer" for Traditional
3. Click "Execute Route Optimizer" for GenAI
4. Compare results

### Test Demand Forecasting
1. Go to Side-by-Side tab
2. Click "Execute Demand Predictor" for Traditional
3. Click "Execute Demand Predictor" for GenAI
4. Compare forecasts and explanations

### Chat with GenAI Agents
1. Go to GenAI Agents tab
2. Scroll to "Chat with AI Agents"
3. Ask questions like:
   - "What's the current system status?"
   - "How can we improve delivery efficiency?"
   - "Analyze the recent route optimization results"

## 🐛 Troubleshooting

### Backend won't start
```bash
# Check if port 5000 is already in use
netstat -ano | findstr :5000

# Kill the process if needed (replace PID)
taskkill /PID <PID> /F

# Verify Python environment
python --version
pip list | findstr flask
```

### Frontend can't connect
```bash
# Check if backend is running
curl http://localhost:5000/api/health

# Check CORS settings in backend/app.py
# Should have: CORS(app)
```

### GenAI agents not available
- Verify Azure OpenAI credentials in `.env`
- Check backend logs for Azure connection errors
- Ensure `ENABLE_GENAI_AGENTS=true`
- Test Azure connection:
  ```bash
  cd backend
  python -c "from ai_agents.azure_openai_service import AzureOpenAIService; s=AzureOpenAIService(); print('✅ Connected')"
  ```

### Traditional agents not available
- Check if `smart_logistics.db` exists
- Verify no import errors in console
- Run: `python test_routes.py` to check registrations

### Still getting 404
1. Check backend is running: `http://localhost:5000/api/health`
2. Verify routes are registered: `python test_routes.py`
3. Test specific endpoint: `curl http://localhost:5000/api/genai-agents/compare`
4. Check browser console for actual URL being called
5. Verify frontend is calling correct port (5000, not 5173)

## 📚 Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Browser (localhost:5173)                 │
│                  React + TypeScript + Vite                   │
└──────────────────────────┬──────────────────────────────────┘
                          │ HTTP Requests
                          ↓
┌─────────────────────────────────────────────────────────────┐
│              Flask Backend (localhost:5000)                  │
├─────────────────────────────────────────────────────────────┤
│  /api/agents/*          │  /api/genai-agents/*              │
│  Traditional AI Agents  │  GenAI Agents                     │
│  ├─ Route Optimizer     │  ├─ Route Optimizer (GPT-4)       │
│  │  (Genetic + OR-Tools)│  │  (Azure OpenAI)                │
│  ├─ Demand Predictor    │  ├─ Demand Predictor (GPT-4)      │
│  │  (LSTM + Stats)      │  │  (Azure OpenAI)                │
│  └─ Orchestrator        │  └─ Orchestrator (GPT-4)          │
└─────────────────────────────────────────────────────────────┘
                          │
                          ↓
              ┌───────────────────────┐
              │  smart_logistics.db   │
              │  (SQLite Database)    │
              └───────────────────────┘
```

## ✅ Success Checklist

- [ ] Backend running on http://localhost:5000
- [ ] Frontend running on http://localhost:5173
- [ ] Can access http://localhost:5000/api/health
- [ ] Can access http://localhost:5000/api/genai-agents/compare
- [ ] Agent Comparison page loads without errors
- [ ] Can see both Traditional and GenAI agent cards
- [ ] Can execute route optimization on both systems
- [ ] Can execute demand forecasting on both systems
- [ ] GenAI chat interface works (if Azure configured)

## 🎉 All Done!

Your Smart Logistics System with AI Agent Comparison is now fully operational!

**Next Steps:**
1. Explore the different agent types
2. Compare performance and decision quality
3. Try the GenAI chat interface
4. Generate reports using AI agents
5. Add your own test scenarios

For more details, see:
- `AGENT_COMPARISON_FIX.md` - Detailed fix documentation
- `docs/AI_AGENTS_DOCUMENTATION.md` - Agent architecture
- `README.md` - Project overview

