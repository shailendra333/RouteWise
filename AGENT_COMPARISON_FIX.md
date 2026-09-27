# 🚀 Quick Start Guide - Agent Comparison Dashboard

## Issue Fixed ✅
The agent comparison dashboard 404 error has been resolved. The issue was:
1. Missing import in `ai_agents/__init__.py` (importing non-existent modules)
2. Backend server was not running

## Solution

### Backend Routes Verified ✅
All required API endpoints are properly registered:
- `/api/agents/status` - Traditional agents status
- `/api/agents/health` - Traditional agents health check
- `/api/genai-agents/status` - GenAI agents status
- `/api/genai-agents/health` - GenAI agents health check
- `/api/genai-agents/compare` - Comparison endpoint

### Steps to Run

#### 1. Start the Backend (REQUIRED)

**Option A: Using Batch File (Easiest)**
```bash
cd backend
start-backend.bat
```

**Option B: Using PowerShell**
```powershell
cd backend
.\start-backend.ps1
```

**Option C: Manual Start**
```bash
cd backend
.\.venv\Scripts\activate
python app.py
```

The backend will start on **http://localhost:5000**

You should see output like:
```
✅ Traditional AI Agents API endpoints registered successfully
✅ GenAI Agents API endpoints registered successfully
 * Running on http://0.0.0.0:5000
```

#### 2. Start the Frontend

In a **new terminal window**:

```bash
cd frontend
npm run dev
```

The frontend will start on **http://localhost:5173**

#### 3. Access the Agent Comparison Dashboard

1. Open your browser to http://localhost:5173
2. Navigate to **AI Agents > Agent Comparison**
3. You should now see:
   - ✅ Traditional agents available
   - ✅ GenAI agents available (if Azure OpenAI is configured)
   - Comparison matrix
   - Ability to execute both agent types side-by-side

## Troubleshooting

### Still Getting 404?

1. **Verify backend is running:**
   ```bash
   curl http://localhost:5000/api/health
   # Should return: {"status": "ok"}
   ```

2. **Check GenAI agents endpoint:**
   ```bash
   curl http://localhost:5000/api/genai-agents/compare
   # Should return comparison data
   ```

3. **Check traditional agents endpoint:**
   ```bash
   curl http://localhost:5000/api/agents/status
   # Should return agent status
   ```

### Azure OpenAI Configuration

Make sure your `.env` file has:
```env
AZURE_OPENAI_API_KEY=your_key_here
AZURE_OPENAI_ENDPOINT=your_endpoint_here
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4.1
AZURE_OPENAI_API_VERSION=2025-01-01-preview
ENABLE_GENAI_AGENTS=true
```

### Traditional Agents Not Available

If traditional agents show as unavailable:
- Restart the backend
- Check backend console for error messages
- Verify database exists: `smart_logistics.db`

### GenAI Agents Not Available

If GenAI agents show as unavailable:
- Check Azure OpenAI credentials in `.env`
- Verify `ENABLE_GENAI_AGENTS=true` in `.env`
- Check backend console for Azure OpenAI connection errors

## Features Available

### Agent Comparison Dashboard
- **Overview Tab**: Compare capabilities of both agent types
- **Traditional Agents Tab**: View and test rule-based agents
- **GenAI Agents Tab**: View and test AI-powered agents
- **Side-by-Side Tab**: Execute same task on both and compare:
  - Execution time
  - Decision quality
  - Explanation style
  - Response format

### Agent Types

**Traditional Agents:**
- Route Optimizer (Genetic Algorithm + OR-Tools)
- Demand Predictor (LSTM + Statistical Methods)
- Fast, deterministic, cost-effective

**GenAI Agents:**
- Route Optimizer (Azure OpenAI GPT-4 powered)
- Demand Predictor (Azure OpenAI GPT-4 powered)
- Natural language explanations
- Context-aware reasoning
- Conversational interface

## Architecture

```
Frontend (React + Vite)
   ↓
   ↓ HTTP Requests
   ↓
Backend (Flask)
   ├── /api/agents/* → Traditional AI Agents
   │   ├── Rule-based logic
   │   ├── Genetic Algorithm
   │   └── LSTM Models
   │
   └── /api/genai-agents/* → GenAI Agents
       ├── Azure OpenAI Integration
       ├── Natural Language Processing
       └── Context-aware reasoning
```

## Testing the Fix

1. Start backend: `cd backend && start-backend.bat`
2. Wait for: "✅ GenAI Agents API endpoints registered successfully"
3. Start frontend: `cd frontend && npm run dev`
4. Open browser: http://localhost:5173
5. Navigate to: AI Agents > Agent Comparison
6. You should see: ✅ Both agent systems available

## Next Steps

- Test route optimization with both agent types
- Test demand forecasting with both agent types
- Compare execution times and explanation quality
- Try the GenAI chat interface
- Generate reports using GenAI agents

Enjoy comparing traditional and GenAI-powered autonomous agents! 🎉

