# AI Agents Quick Start Guide

## 🚀 Get Started with AI Agents in 5 Minutes

### What are AI Agents?

AI Agents are autonomous software entities that can:
- **Perceive** their environment (traffic, demand, orders)
- **Decide** the best course of action
- **Act** on those decisions automatically
- **Learn** from outcomes to improve over time

---

## Step 1: Start the Backend

```bash
cd backend
python app.py
```

You should see:
```
✓ AI Agents API endpoints registered successfully
 * Running on http://127.0.0.1:5000
```

---

## Step 2: Check Agents Health

```bash
curl http://localhost:5000/api/agents/health
```

**Expected Response:**
```json
{
  "status": "healthy",
  "timestamp": "2026-02-13T10:30:00",
  "agents": {
    "orchestrator": {
      "status": "idle",
      "agent_id": "orchestrator_001"
    },
    "agents": {
      "route_optimizer": {
        "status": "idle",
        "tasks_completed": 0
      },
      "demand_predictor": {
        "status": "idle",
        "tasks_completed": 0
      }
    }
  }
}
```

---

## Step 3: Test Route Optimization Agent

Create a file `test_route_agent.py`:

```python
import requests
import json

# Prepare test data
data = {
    "current_routes": [
        {
            "route_id": 1,
            "deliveries": [
                {"id": 1, "lat": 40.7829, "lon": -73.9654, "priority": "normal"},
                {"id": 2, "lat": 40.7580, "lon": -73.9855, "priority": "normal"},
                {"id": 3, "lat": 40.7614, "lon": -73.9776, "priority": "urgent"}
            ],
            "efficiency": 0.65
        }
    ],
    "traffic_data": {
        "congestion_level": "high"
    }
}

# Call Route Optimizer Agent
response = requests.post(
    'http://localhost:5000/api/agents/route-optimizer/execute',
    json=data
)

result = response.json()

# Print results
print("✓ Route Optimization Complete!")
print(f"Success: {result['success']}")
print(f"Execution Time: {result['result']['execution_time']:.2f}s")

if result['result']['result']['success']:
    improvements = result['result']['result']['improvements']
    print(f"\n📊 Improvements:")
    print(f"  - Routes optimized: {improvements.get('total_routes_optimized', 0)}")
    print(f"  - Time saved: {improvements.get('estimated_time_saved', 0)} minutes")
    print(f"  - Cost saved: ${improvements.get('estimated_cost_saved', 0)}")
```

Run it:
```bash
python test_route_agent.py
```

**Expected Output:**
```
✓ Route Optimization Complete!
Success: True
Execution Time: 0.15s

📊 Improvements:
  - Routes optimized: 2
  - Time saved: 25 minutes
  - Cost saved: $50
```

---

## Step 4: Test Demand Prediction Agent

Create `test_demand_agent.py`:

```python
import requests
from datetime import datetime, timedelta

# Simulate historical orders
historical_orders = []
for i in range(30):
    date = (datetime.now() - timedelta(days=30-i)).strftime('%Y-%m-%d')
    # Simulate varying demand (100-150 orders per day)
    for j in range(100 + (i % 50)):
        historical_orders.append({
            'id': len(historical_orders) + 1,
            'order_date': date,
            'quantity': 1
        })

# Prepare data
data = {
    "historical_orders": historical_orders,
    "current_capacity": {
        "vehicles": 10,
        "drivers": 10,
        "deliveries_per_vehicle": 30
    },
    "external_factors": {
        "weather": {"condition": "clear"},
        "events": ["sports_game"],
        "holidays": []
    }
}

# Call Demand Predictor Agent
response = requests.post(
    'http://localhost:5000/api/agents/demand-predictor/execute',
    json=data
)

result = response.json()

# Print forecasts
print("✓ Demand Forecasting Complete!")
print(f"Success: {result['success']}")

agent_result = result['result']['result']
forecasts = agent_result.get('forecasts_generated', 0)
print(f"\n📈 Generated {forecasts} forecasts:")

# Show first 3 days
if 'result' in agent_result and 'forecasts' in agent_result['result']:
    for forecast in agent_result['result']['forecasts'][:3]:
        print(f"\n  {forecast['date']}:")
        print(f"    Predicted Demand: {forecast['predicted_demand']:.0f} orders")
        print(f"    Confidence Range: {forecast['confidence_lower']:.0f} - {forecast['confidence_upper']:.0f}")
```

Run it:
```bash
python test_demand_agent.py
```

**Expected Output:**
```
✓ Demand Forecasting Complete!
Success: True

📈 Generated 7 forecasts:

  2026-02-14:
    Predicted Demand: 125 orders
    Confidence Range: 106 - 144

  2026-02-15:
    Predicted Demand: 131 orders
    Confidence Range: 111 - 151

  2026-02-16:
    Predicted Demand: 137 orders
    Confidence Range: 116 - 158
```

---

## Step 5: Orchestrate Multiple Agents

Create `test_orchestrator.py`:

```python
import requests

# Complex scenario requiring multiple agents
data = {
    "current_routes": [
        {
            "route_id": 1,
            "deliveries": [{"id": i} for i in range(10)],
            "efficiency": 0.7
        }
    ],
    "historical_orders": [{"id": i} for i in range(100)],
    "traffic_data": {"congestion_level": "medium"},
    "external_factors": {"weather": {"condition": "clear"}},
    "current_capacity": {"vehicles": 10, "drivers": 10}
}

# Let orchestrator coordinate agents
response = requests.post(
    'http://localhost:5000/api/agents/orchestrate',
    json=data
)

result = response.json()

print("✓ Orchestration Complete!")
print(f"Success: {result['success']}")

orch_result = result['orchestration_result']
print(f"\n🤖 Agent Coordination:")
print(f"  - Tasks executed: {len(orch_result['executed_tasks'])}")
print(f"  - Agents involved: {len(orch_result['agent_results'])}")

outcome = orch_result.get('coordination_outcome', {})
if outcome:
    print(f"\n📊 Coordination Results:")
    print(f"  - Success rate: {outcome.get('success_rate', 0) * 100:.0f}%")
    print(f"  - Efficiency: {outcome.get('coordination_efficiency', 0) * 100:.0f}%")
```

Run it:
```bash
python test_orchestrator.py
```

---

## Step 6: Simulate Scenarios

```python
import requests

scenarios = ['high_demand', 'traffic_congestion', 'emergency']

for scenario in scenarios:
    print(f"\n🎯 Testing scenario: {scenario}")
    
    response = requests.post(
        'http://localhost:5000/api/agents/simulate',
        json={'scenario': scenario, 'parameters': {}}
    )
    
    result = response.json()
    
    if result['success']:
        insights = result['insights']
        print(f"  ✓ Agents activated: {insights['agents_activated']}")
        print(f"  ✓ Execution time: {insights['execution_time']:.2f}s")
        print(f"  ✓ Recommendations: {len(insights['recommendations'])}")
```

---

## Step 7: Monitor Agent Performance

```python
import requests

# Get overall status
response = requests.get('http://localhost:5000/api/agents/status')
status = response.json()

print("📊 Agent Performance Metrics:\n")

for agent_name, agent_data in status['status']['agents'].items():
    metrics = agent_data.get('metrics', {})
    print(f"{agent_name}:")
    print(f"  Tasks completed: {metrics.get('tasks_completed', 0)}")
    print(f"  Success rate: {metrics.get('success_rate', 0) * 100:.1f}%")
    print(f"  Avg execution time: {metrics.get('average_execution_time', 0):.2f}s")
    print()
```

---

## Understanding Agent Results

### Route Optimizer Output
```json
{
  "improvements": {
    "average_improvement": 0.25,        // 25% improvement
    "total_routes_optimized": 2,        // 2 routes optimized
    "estimated_time_saved": 30,         // 30 minutes saved
    "estimated_cost_saved": 50          // $50 saved
  }
}
```

### Demand Predictor Output
```json
{
  "forecasts": [
    {
      "date": "2026-02-14",
      "predicted_demand": 125.5,
      "confidence_lower": 106.3,
      "confidence_upper": 144.7,
      "confidence_level": 0.95
    }
  ]
}
```

---

## Next Steps

1. **Integrate with Frontend**: Display agent insights in dashboard
2. **Real-time Updates**: Use WebSockets for live agent status
3. **Custom Agents**: Create domain-specific agents
4. **Production Deploy**: Deploy with proper monitoring

---

## Troubleshooting

**Agent not responding?**
```bash
# Check agent health
curl http://localhost:5000/api/agents/health
```

**Getting errors?**
```bash
# Check backend logs
tail -f backend/app.log
```

**Want to see agent memory?**
```bash
curl http://localhost:5000/api/agents/agent/route_optimizer_001/memory
```

---

## Learn More

- 📖 [Full AI Agents Documentation](AI_AGENTS_DOCUMENTATION.md)
- 📚 [Improvements Guide](IMPROVEMENTS_AND_AI_AGENTS.md)
- 🔧 [API Reference](API_DOCUMENTATION.md)

---

**Congratulations!** 🎉 You now have autonomous AI agents running in your Smart Logistics System!

