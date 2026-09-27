# 🚀 AI AGENTS WITH TEST DATA - QUICK START GUIDE

## 🎯 What's New

### ✅ Automatic Test Data Generation
- **2,000+ orders** automatically seeded on first startup
- **200 optimized routes** with different algorithms
- **150 demand forecasts** for next 30 days
- **NYC-based locations** across 5 zones (A-E)
- **90 days** of historical data

### ✅ New UI Page: AI Agents Dashboard
- **Real-time agent monitoring** - See all agents in action
- **Execute agent actions** - Click buttons to run agents
- **Activity logs** - Watch agents work in real-time
- **Performance statistics** - Track success rates and execution times
- **Scenario simulation** - Test high_demand, traffic, emergency scenarios

### ✅ Database Activity Logging
- All agent actions are logged to database
- View complete history of agent decisions
- Track performance over time
- Analyze agent behavior patterns

---

## 🚀 GETTING STARTED (5 Minutes)

### Step 1: Start Backend
```bash
cd backend
python app.py
```

**What happens:**
- ✅ Database tables created automatically
- ✅ **2,000+ orders** inserted automatically (first run only)
- ✅ 200 routes and 150 forecasts added
- ✅ AI Agents system initialized
- ✅ API server running on http://localhost:5000

**You'll see:**
```
📊 Database is empty. Seeding test data...
🚀 Generating test data...
✅ Generated 1847 orders
✅ Generated 200 routes
✅ Generated 150 forecasts
✅ Test data seeded: 1847 orders, 200 routes, 150 forecasts
 * Running on http://127.0.0.1:5000
✓ AI Agents API endpoints registered successfully
```

### Step 2: Start Frontend
```bash
# In a new terminal
npm run dev
```

**Access:** http://localhost:5173

### Step 3: Visit AI Agents Dashboard
1. Login with:
   - Email: `demo@smartlogistics.com`
   - Password: `demo123`

2. Click **"AI Agents"** in the navigation menu

3. You'll see:
   - 🤖 3 AI agents (Route Optimizer, Demand Predictor, Orchestrator)
   - ⚡ Action buttons to execute agents
   - 📊 Real-time statistics
   - 📋 Activity logs

---

## 🎮 HOW TO USE THE AI AGENTS UI

### Execute Actions

#### 1. **Optimize Routes**
```
Click: "Optimize Routes" button
What it does:
- Fetches 10 real orders from database
- Analyzes traffic conditions
- Optimizes delivery sequence
- Saves results to agent_logs table
- Shows time/cost savings

Result: "✅ Route optimization complete!"
```

#### 2. **Forecast Demand**
```
Click: "Forecast Demand" button
What it does:
- Analyzes 100 historical orders
- Predicts next 7 days demand
- Detects anomalies
- Recommends capacity changes
- Logs forecasts

Result: "✅ Demand forecasting complete!"
```

#### 3. **Simulate Scenario**
```
Click: "Simulate Scenario" button
What it does:
- Tests high_demand scenario
- Coordinates multiple agents
- Shows system response
- Logs all actions

Result: "✅ high_demand scenario simulation complete!"
```

### Monitor Activity

**Real-time Activity Log:**
- Shows every agent action
- Success/failure status
- Execution time
- Timestamp
- Auto-refreshes every 5 seconds

**Performance Statistics:**
- Total actions per agent
- Success rate percentage
- Average execution time
- Historical trends

---

## 🧪 TESTING WITH PYTHON SCRIPT

### Run Comprehensive Tests
```bash
cd backend
python test_agents.py
```

**This will:**
1. ✅ Check system health
2. ✅ Display database statistics (2000+ orders)
3. ✅ Show agent status
4. ✅ Execute route optimization
5. ✅ Execute demand forecasting
6. ✅ Run scenario simulations
7. ✅ Display activity logs
8. ✅ Show performance stats

**Expected Output:**
```
🤖 ========================================================== 🤖
  AI AGENTS SYSTEM - COMPREHENSIVE TEST SUITE
🤖 ========================================================== 🤖

============================================================
  1. HEALTH CHECK
============================================================

✅ System Status: healthy
✅ AI Agents Status: healthy

============================================================
  2. DATABASE STATISTICS
============================================================

📦 Total Orders: 1847
🚛 Total Routes: 200
📈 Total Forecasts: 150
🤖 Agent Logs: 5

📊 Orders by Zone:
   Zone A: 412 orders
   Zone B: 389 orders
   Zone C: 401 orders
   Zone D: 354 orders
   Zone E: 291 orders

... (more test results)
```

---

## 📊 DATABASE SCHEMA

### New Tables

#### agent_logs
```sql
CREATE TABLE agent_logs (
    log_id INTEGER PRIMARY KEY,
    agent_id TEXT NOT NULL,
    agent_name TEXT NOT NULL,
    action TEXT NOT NULL,
    result TEXT,
    success BOOLEAN NOT NULL,
    execution_time REAL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Sample Data Distribution

**Orders (1800-2000 total):**
- Zone A (Manhattan): ~400 orders
- Zone B (Brooklyn): ~400 orders
- Zone C (Queens): ~400 orders
- Zone D (Bronx): ~350 orders
- Zone E (Staten Island): ~300 orders
- Date range: Last 90 days
- Weekday bias: More orders Mon-Fri

**Routes (200 total):**
- Vehicle IDs: 1-20
- Stops per route: 5-15
- Distance: 15-120 km
- Time: 75-450 minutes
- Algorithms: genetic, ortools, hybrid

**Forecasts (150 total):**
- Products: PROD-001 to PROD-005
- Forecast period: Next 30 days
- Includes confidence intervals
- Model versions: v1.0, v2.0, v3.0

---

## 🎯 WHAT TO DO NEXT

### Explore the Data
```python
# In Python
import sqlite3
conn = sqlite3.connect('smart_logistics.db')

# View orders
import pandas as pd
orders = pd.read_sql("SELECT * FROM orders LIMIT 10", conn)
print(orders)

# View routes
routes = pd.read_sql("SELECT * FROM optimized_routes LIMIT 10", conn)
print(routes)
```

### Use Other Pages
1. **Dashboard** - View system metrics with real data
2. **Data Management** - Export/import the test data
3. **Route Optimization** - Use ML algorithms on test orders
4. **Demand Forecasting** - Train LSTM on 2000+ orders
5. **Analytics** - Analyze patterns in test data

### Experiment with Agents
```bash
# Try different scenarios
curl -X POST http://localhost:5000/api/agents/simulate \
  -H "Content-Type: application/json" \
  -d '{"scenario": "traffic_congestion", "parameters": {}}'

# Check agent memory
curl http://localhost:5000/api/agents/agent/route_optimizer_001/memory

# Get detailed metrics
curl http://localhost:5000/api/agents/agent/demand_predictor_001/metrics
```

---

## 🔧 CUSTOMIZATION

### Generate More Test Data
```python
from test_data_generator import insert_test_data

# Generate 5000 orders
insert_test_data(num_orders=5000, days_back=180)
```

### Reset Database
```bash
# Delete database file
rm smart_logistics.db

# Restart backend (will regenerate)
python app.py
```

### Modify Test Data
Edit `backend/test_data_generator.py`:
- Add more locations
- Change product catalog
- Adjust order frequency
- Modify date ranges

---

## 📈 KEY FEATURES

### Realistic Data
- ✅ NYC geographic coordinates
- ✅ Weekday/weekend patterns
- ✅ Business hours delivery times
- ✅ Zone-based distribution
- ✅ Multiple products and customers

### Automatic Seeding
- ✅ Runs only once on empty database
- ✅ No manual intervention needed
- ✅ Fast generation (< 10 seconds)
- ✅ Validates all data before insertion

### Agent Integration
- ✅ All agents work with real data
- ✅ Actions logged to database
- ✅ Performance tracked automatically
- ✅ Statistics updated in real-time

---

## 🎉 SUCCESS METRICS

After running the system, you should see:

✅ **Database:** 2000+ orders, 200 routes, 150 forecasts  
✅ **AI Agents:** 3 agents active and healthy  
✅ **UI:** AI Agents dashboard showing real-time activity  
✅ **Logs:** Agent actions being recorded  
✅ **Statistics:** Success rates and execution times  

---

## 🆘 TROUBLESHOOTING

### Database not seeding?
```bash
# Check if database exists
ls smart_logistics.db

# Force regenerate
rm smart_logistics.db
python app.py
```

### Agents not working?
```bash
# Check agents health
curl http://localhost:5000/api/agents/health

# Check logs
tail -f backend/app.log
```

### UI not showing data?
```bash
# Check API connection
curl http://localhost:5000/api/database-stats

# Verify frontend is running
curl http://localhost:5173
```

---

## 📚 API ENDPOINTS

### Database
- `GET /api/database-stats` - Get counts and statistics
- `GET /api/data-preview?type=orders&limit=50` - Preview data

### AI Agents
- `GET /api/agents/health` - Check agents status
- `GET /api/agents/status` - Get all agent metrics
- `GET /api/agents/activity?limit=20` - Get recent logs
- `GET /api/agents/statistics` - Get performance stats
- `POST /api/agents/route-optimizer/execute` - Run route optimizer
- `POST /api/agents/demand-predictor/execute` - Run demand predictor
- `POST /api/agents/simulate` - Run scenario simulation

---

## 🎊 ENJOY!

You now have:
- ✅ 2000+ test orders ready to use
- ✅ 3 AI agents working autonomously
- ✅ Interactive UI dashboard
- ✅ Real-time activity monitoring
- ✅ Complete test suite

**Visit http://localhost:5173/ai-agents and start exploring!** 🚀

---

**Questions?** Check the main documentation or run `python test_agents.py` to verify everything works!

