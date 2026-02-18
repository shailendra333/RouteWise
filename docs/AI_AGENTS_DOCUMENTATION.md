# AI Agents System Documentation

## 🤖 Overview

The Smart Logistics System now includes an advanced **AI Agents** framework that enables autonomous, intelligent decision-making for logistics operations. The system uses multiple specialized agents that perceive, decide, act, and learn from their environment.

## 🏗️ Architecture

### Agent Hierarchy

```
┌─────────────────────────────────────────────────────────────┐
│                   Orchestrator Agent                        │
│  (Coordinates all agents and manages high-level decisions)  │
└───────────────┬──────────────────┬─────────────────────────┘
                │                  │
    ┌───────────▼──────────┐  ┌────▼────────────────────┐
    │  Route Optimizer     │  │  Demand Predictor       │
    │      Agent           │  │      Agent              │
    └──────────────────────┘  └─────────────────────────┘
            │                           │
            │                           │
    ┌───────▼──────────┐      ┌────────▼────────────┐
    │  • Traffic       │      │  • Forecasting      │
    │  • Rerouting     │      │  • Capacity Plan    │
    │  • Optimization  │      │  • Anomaly Detect   │
    └──────────────────┘      └─────────────────────┘
```

## 🧠 Agent Capabilities

### 1. **Base Agent** (Abstract)
All agents inherit from `BaseAgent` which provides:

- **Memory System**: Short-term and long-term memory with pattern extraction
- **Perception**: Extract relevant information from environment
- **Decision Making**: Decide actions based on perception
- **Action Execution**: Execute decided actions
- **Learning**: Learn from experiences and update knowledge
- **Performance Tracking**: Monitor success rates and execution times

**Key Methods:**
```python
perceive(environment: Dict) -> Dict     # Observe environment
decide(perception: Dict) -> Dict        # Make decisions
act(decision: Dict) -> Dict             # Execute actions
learn(experience: Dict)                 # Learn from results
execute_task(environment: Dict) -> Dict # Full agent cycle
```

### 2. **Route Optimizer Agent**
Autonomous route optimization and dynamic routing decisions.

**Capabilities:**
- Real-time route optimization
- Dynamic rerouting based on traffic
- Priority delivery handling
- Traffic analysis and congestion detection
- Multi-objective optimization

**Use Cases:**
- Responding to traffic congestion
- Handling urgent deliveries
- Optimizing inefficient routes
- Minimizing delivery times and costs

**Example Environment:**
```python
{
    "current_routes": [
        {
            "route_id": 1,
            "deliveries": [...],
            "efficiency": 0.75
        }
    ],
    "traffic_data": {
        "congestion_level": "medium"
    },
    "delivery_status": {...}
}
```

**Example Output:**
```python
{
    "success": True,
    "executed_actions": [
        {
            "type": "reroute",
            "improvement": 0.25,
            "time_saved": 15  # minutes
        }
    ],
    "improvements": {
        "average_improvement": 0.25,
        "estimated_time_saved": 30,
        "estimated_cost_saved": 50
    }
}
```

### 3. **Demand Predictor Agent**
Proactive demand forecasting and capacity planning.

**Capabilities:**
- 7-day demand forecasting
- Capacity utilization analysis
- Anomaly detection (spikes/drops)
- Trend identification
- Resource allocation recommendations

**Use Cases:**
- Predicting demand spikes
- Planning resource allocation
- Detecting unusual patterns
- Capacity planning
- Seasonal trend analysis

**Example Environment:**
```python
{
    "historical_orders": [...],  # Past 30+ days
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
```

**Example Output:**
```python
{
    "forecasts_generated": 7,
    "forecasts": [
        {
            "date": "2026-02-14",
            "predicted_demand": 325.5,
            "confidence_lower": 285.3,
            "confidence_upper": 365.7,
            "confidence_level": 0.95
        }
    ],
    "recommendations": [
        {
            "type": "capacity_increase",
            "recommended_increase": 0.15
        }
    ],
    "alerts": [...]
}
```

### 4. **Orchestrator Agent**
Master coordinator that manages multiple agents.

**Capabilities:**
- Agent coordination and task delegation
- Priority management
- Conflict resolution
- Strategic planning
- System health monitoring

**Use Cases:**
- Coordinating multiple optimization tasks
- Managing complex scenarios
- Balancing agent workloads
- System-wide decision making

## 🚀 API Endpoints

### Health Check
```http
GET /api/agents/health
```

**Response:**
```json
{
    "status": "healthy",
    "timestamp": "2026-02-13T10:30:00",
    "agents": {
        "orchestrator": {...},
        "agents": {
            "route_optimizer": {...},
            "demand_predictor": {...}
        }
    }
}
```

### Orchestrate Multiple Agents
```http
POST /api/agents/orchestrate
Content-Type: application/json

{
    "current_routes": [...],
    "historical_orders": [...],
    "traffic_data": {...},
    "external_factors": {...}
}
```

**Response:**
```json
{
    "success": true,
    "orchestration_result": {
        "executed_tasks": [...],
        "agent_results": {...},
        "coordination_outcome": {
            "success_rate": 1.0,
            "total_tasks": 2
        }
    }
}
```

### Execute Route Optimizer
```http
POST /api/agents/route-optimizer/execute
Content-Type: application/json

{
    "current_routes": [...],
    "traffic_data": {...}
}
```

### Execute Demand Predictor
```http
POST /api/agents/demand-predictor/execute
Content-Type: application/json

{
    "historical_orders": [...],
    "current_capacity": {...}
}
```

### Get Agent Status
```http
GET /api/agents/status
```

### Get Agent Metrics
```http
GET /api/agents/agent/<agent_id>/metrics
```

**Response:**
```json
{
    "success": true,
    "agent_id": "route_optimizer_001",
    "metrics": {
        "tasks_completed": 150,
        "tasks_failed": 5,
        "success_rate": 0.968,
        "average_execution_time": 1.25
    }
}
```

### Get Agent Memory
```http
GET /api/agents/agent/<agent_id>/memory?limit=10
```

### Simulate Scenario
```http
POST /api/agents/simulate
Content-Type: application/json

{
    "scenario": "high_demand",
    "parameters": {
        "vehicles": 10,
        "drivers": 10
    }
}
```

**Scenarios:**
- `high_demand`: Simulate demand spike
- `traffic_congestion`: Simulate heavy traffic
- `emergency`: Simulate emergency orders

## 💡 Usage Examples

### Example 1: Optimize Routes with Traffic

```python
import requests

# Prepare environment data
data = {
    "current_routes": [
        {
            "route_id": 1,
            "deliveries": [
                {"id": 1, "lat": 40.7829, "lon": -73.9654},
                {"id": 2, "lat": 40.7580, "lon": -73.9855}
            ],
            "efficiency": 0.65
        }
    ],
    "traffic_data": {
        "congestion_level": "high"
    }
}

# Execute route optimizer
response = requests.post(
    'http://localhost:5000/api/agents/route-optimizer/execute',
    json=data
)

result = response.json()
print(f"Optimization success: {result['success']}")
print(f"Time saved: {result['result']['improvements']['estimated_time_saved']} min")
```

### Example 2: Get Demand Forecast

```python
import requests

# Prepare historical data
data = {
    "historical_orders": [
        {"order_date": "2026-02-01", "quantity": 100},
        {"order_date": "2026-02-02", "quantity": 105},
        # ... more historical data
    ],
    "current_capacity": {
        "vehicles": 10,
        "drivers": 10,
        "deliveries_per_vehicle": 30
    },
    "external_factors": {
        "weather": {"condition": "clear"},
        "events": [],
        "holidays": []
    }
}

# Execute demand predictor
response = requests.post(
    'http://localhost:5000/api/agents/demand-predictor/execute',
    json=data
)

result = response.json()
forecasts = result['result']['result']

# Print 7-day forecast
for forecast in forecasts:
    print(f"{forecast['date']}: {forecast['predicted_demand']:.0f} orders")
```

### Example 3: Orchestrate Multiple Agents

```python
import requests

# Complex scenario with multiple optimization needs
data = {
    "current_routes": [...],        # Active routes needing optimization
    "historical_orders": [...],     # For demand forecasting
    "traffic_data": {...},          # Real-time traffic
    "external_factors": {...},      # Weather, events, etc.
    "pending_orders": [...],        # Orders to be scheduled
    "current_capacity": {...}       # Available resources
}

# Let orchestrator coordinate agents
response = requests.post(
    'http://localhost:5000/api/agents/orchestrate',
    json=data
)

result = response.json()
print(f"Tasks executed: {len(result['orchestration_result']['executed_tasks'])}")
print(f"Success rate: {result['orchestration_result']['coordination_outcome']['success_rate']}")
```

### Example 4: Simulate High Demand Scenario

```python
import requests

# Simulate what happens during demand spike
data = {
    "scenario": "high_demand",
    "parameters": {
        "vehicles": 10,
        "drivers": 10
    }
}

response = requests.post(
    'http://localhost:5000/api/agents/simulate',
    json=data
)

result = response.json()
insights = result['insights']
print(f"Agents activated: {insights['agents_activated']}")
print(f"Recommendations: {len(insights['recommendations'])}")
```

## 🔄 Agent Lifecycle

### 1. Perception Phase
- Agent observes environment
- Extracts relevant information
- Identifies patterns and anomalies

### 2. Decision Phase
- Analyzes perceived information
- Retrieves relevant memories
- Generates action plan with confidence score

### 3. Action Phase
- Executes decided actions
- Monitors execution
- Collects results

### 4. Learning Phase
- Stores experience in memory
- Updates performance metrics
- Extracts patterns for future use

## 📊 Performance Metrics

Each agent tracks:
- **Tasks Completed**: Total successful tasks
- **Tasks Failed**: Total failed tasks
- **Success Rate**: Percentage of successful tasks
- **Average Execution Time**: Mean time per task
- **Memory Size**: Short-term and long-term memory usage

## 🔧 Extending the System

### Adding a New Agent

```python
from ai_agents.base_agent import BaseAgent

class CustomAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            agent_id="custom_001",
            name="Custom Agent",
            capabilities=["custom_capability"]
        )
    
    def perceive(self, environment):
        # Implement perception logic
        return {"data": "perceived"}
    
    def decide(self, perception):
        # Implement decision logic
        return {"action": "decided"}
    
    def act(self, decision):
        # Implement action logic
        return {"success": True}

# Register with orchestrator
from ai_agents.orchestrator_agent import OrchestratorAgent

orch = OrchestratorAgent()
orch.add_agent('custom', CustomAgent())
```

## 🎯 Best Practices

1. **Environment Data**: Provide complete environment data for best results
2. **Error Handling**: Always check `success` field in responses
3. **Monitoring**: Regularly check agent metrics and status
4. **Memory Management**: Agents auto-manage memory, but monitor size
5. **Confidence Scores**: Use confidence scores to determine action criticality
6. **Simulation**: Test scenarios before production deployment

## 🚀 Future Enhancements

- **Fleet Manager Agent**: Vehicle health monitoring and maintenance
- **Customer Service Agent**: Chatbot for tracking and support
- **Pricing Agent**: Dynamic pricing based on demand
- **Inventory Agent**: Stock level optimization
- **Driver Assistant Agent**: Real-time driver guidance
- **Multi-Agent Reinforcement Learning**: Collaborative learning
- **Explainable AI**: Decision transparency and interpretability

## 📞 Support

For questions or issues with AI Agents:
- Check agent status: `GET /api/agents/status`
- Review agent metrics: `GET /api/agents/agent/<id>/metrics`
- Examine agent memory: `GET /api/agents/agent/<id>/memory`
- Check logs for detailed error messages

---

**Smart Logistics AI Agents** - Autonomous intelligence for modern logistics operations.

