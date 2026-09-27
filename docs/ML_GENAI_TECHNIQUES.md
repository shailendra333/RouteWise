# Machine Learning & GenAI Techniques in the Smart Logistics Showcase

This document summarizes the AI/ML techniques found in `backend/` and how each is
applied to logistics problems (demand planning, routing, and continuous improvement).

## 1. LSTM Neural Networks — Demand Forecasting
**File:** `backend/lstm_forecasting.py` (`AdvancedLSTMForecaster`, TensorFlow/Keras)

- Deep, stacked **LSTM (Long Short-Term Memory)** network (3 LSTM layers + BatchNorm +
  Dropout + Dense layers) that learns temporal dependencies in order/demand history.
- Rich feature engineering: cyclical time encodings (sin/cos of month & weekday),
  **lag features** (1/7/14/30-day), and **rolling statistics** (mean/std/min/max over
  7/14/30-day windows) — classic time-series feature engineering paired with deep learning.
- Predicts a **multi-day horizon** (default 7 days) with confidence intervals (±1.96·σ).
- **Logistics usage:** forecasts parcel/order volume so the business can pre-position
  vehicles, drivers, and warehouse capacity before demand spikes (e.g., holidays, promos),
  reducing missed SLAs and idle-fleet cost.

## 2. Genetic Algorithm — Vehicle Routing / TSP Optimization
**File:** `backend/genetic_algorithm.py` (`GeneticAlgorithmTSP`)

- Classic **evolutionary optimization** applied to the Traveling Salesman Problem:
  population of candidate routes, **tournament selection + elitism**, **Order Crossover
  (OX)** breeding, and **swap mutation**, evolved over generations to minimize total
  distance.
- Tracks best/average distance per generation for convergence analysis.
- **Logistics usage:** used as the metaheuristic route optimizer (and as a fallback
  when Google **OR-Tools** isn't available) to sequence multi-stop deliveries so drivers
  travel the shortest/cheapest path, cutting fuel cost and delivery time.

## 3. Constraint-Programming Route Solver — OR-Tools VRP
**File:** `backend/app.py` (imports `ortools.constraint_solver.pywrapcp`/`routing_enums_pb2`)

- Google **OR-Tools Vehicle Routing solver**, a constraint-programming/metaheuristic
  engine (first-solution strategies + local search) for exact/near-optimal multi-vehicle
  routing with capacity/time-window constraints.
- **Logistics usage:** primary production-grade route optimizer for real fleets with
  multiple vehicles, capacities, and delivery time windows; the genetic algorithm acts
  as a lightweight fallback.

## 4. Geographic Clustering — DBSCAN
**File:** `backend/ai_agents/advanced_learning_engine.py`

- **DBSCAN** (density-based clustering, scikit-learn) groups delivery points that are
  geographically close (`eps` ≈ 5 km) into clusters, using `scipy.spatial.distance.cdist`
  for pairwise distance calculations.
- **Logistics usage:** identifies natural delivery zones/hubs so routes and driver
  assignments can be optimized per cluster (zone-based dispatching), and helps detect
  where new micro-hubs would reduce travel distance.

## 5. Multi-Objective Optimization & Statistical Pattern Learning
**Files:** `backend/ai_agents/advanced_learning_engine.py`, `backend/ai_agents/learning_engine.py`

- Weighted **multi-objective scoring** (time saved, cost saved, customer satisfaction)
  normalizes and combines competing KPIs into a single optimization score, enabling
  trade-off-aware decision ranking.
- **Online/incremental learning loop:** every routing decision and its real-world
  outcome are logged; the engine recomputes rolling **confidence scores**
  (successes/total observations), builds "pattern signatures" (conditions → outcome),
  and only trusts patterns once a confidence threshold (≥0.6) and minimum observation
  count are met — a lightweight, interpretable analogue to reinforcement learning's
  reward-based policy refinement, backed by SQLite as the experience store.
- Includes seasonal-pattern detection (90-day windows) and "what-if" scenario/auto-tuning
  utilities (Phase 2/3 features).
- **Logistics usage:** continuously improves routing/demand rules from operational
  feedback (e.g., "reroute during rain adds +12 min but +0.4 satisfaction") without
  manual retraining, and prioritizes recommendations that best balance cost, speed, and
  customer experience.

## 6. Anomaly & Trend Detection (Statistical)
**File:** `backend/ai_agents/demand_predictor_agent.py`

- Simple but effective **statistical anomaly detection**: compares short-term (7-day)
  vs. long-term (30-day) averages, flags spikes/drops beyond a threshold ratio, and
  computes week-over-week trend direction/magnitude.
- **Logistics usage:** triggers proactive alerts (e.g., "demand spike detected") and
  capacity-planning recommendations (extra vehicles/drivers) before problems occur.

## 7. Multi-Agent System (Perceive → Decide → Act → Learn)
**Files:** `backend/ai_agents/base_agent.py`, `route_optimizer_agent.py`,
`demand_predictor_agent.py`, `orchestrator_agent.py`

- Classic **agentic architecture**: each agent implements a perceive/decide/act loop,
  maintains short-term + long-term memory, tracks performance metrics/success rate, and
  an `OrchestratorAgent` coordinates task delegation, prioritization, and conflict
  resolution across specialized agents (routing, demand).
- **Logistics usage:** decouples concerns (route optimization vs. demand forecasting)
  while allowing a central coordinator to sequence/parallelize work and resolve
  competing priorities (e.g., urgent delivery vs. traffic rerouting).

## 8. GenAI (Azure OpenAI / GPT-4) — Reasoning, Explanation & Conversational AI
**Files:** `backend/ai_agents/azure_openai_service.py`, `genai_demand_predictor_agent.py`,
`genai_route_optimizer_agent.py`, `genai_orchestrator.py`, `genai_agents_api.py`

- Wraps **Azure OpenAI (GPT-4)** chat completions with structured **JSON-mode prompting**
  for: situation analysis (`analyze_situation`), outcome prediction, natural-language
  decision explanations (`generate_explanation`), markdown report generation
  (`generate_report`), and a contextual chat assistant (`chat_with_context`).
- **GenAI-augmented agents** mirror the classic ML agents but replace/augment
  statistical logic with **LLM reasoning**: e.g. `GenAIDemandPredictorAgent` blends
  numeric trend stats with an LLM-generated 7-day forecast plus natural-language
  insights/risks, and `GenAIOrchestrator` uses LLM reasoning to coordinate agents based
  on textual system state rather than hard-coded rules.
- **Logistics usage:** turns opaque numeric predictions/decisions into human-readable
  explanations for dispatchers/managers ("why was this route changed?"), generates
  executive summaries/reports, and enables natural-language Q&A over live logistics
  data — improving trust, adoption, and explainability of the ML layer.

---

### Summary Table

| Technique | Type | Library | Logistics Use Case |
|---|---|---|---|
| LSTM | Deep Learning (time series) | TensorFlow/Keras | Demand forecasting |
| Genetic Algorithm (TSP) | Evolutionary optimization | NumPy | Route sequencing / fallback optimizer |
| VRP Solver | Constraint programming | Google OR-Tools | Multi-vehicle route optimization |
| DBSCAN | Unsupervised clustering | scikit-learn | Delivery zone/hub clustering |
| Multi-objective scoring + pattern learning | Statistical/online learning | NumPy, SQLite | Continuous decision improvement |
| Trend/anomaly detection | Statistical analysis | NumPy | Demand spike/drop alerts |
| Multi-agent orchestration | Agentic architecture | Custom | Coordinated autonomous decision-making |
| Azure OpenAI GPT-4 | Generative AI / LLM | `openai` SDK | Explanations, reports, conversational insights, LLM-based forecasting/orchestration |
