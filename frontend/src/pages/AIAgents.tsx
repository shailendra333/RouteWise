import React, { useState, useEffect } from 'react';
import { Activity, Bot, TrendingUp, Route, Brain, Zap, Clock, CheckCircle, XCircle, Sparkles, ArrowRight } from 'lucide-react';
import axios from 'axios';
import { Link } from 'react-router-dom';

interface AgentStatus {
  agent_id: string;
  name: string;
  status: string;
  capabilities: string[];
  metrics: {
    tasks_completed: number;
    tasks_failed: number;
    success_rate: number;
    average_execution_time: number;
  };
}

interface AgentLog {
  agent_id: string;
  agent_name: string;
  action: string;
  result: string;
  success: boolean;
  execution_time: number;
  timestamp: string;
}

interface AgentStats {
  total_actions: number;
  successful_actions: number;
  success_rate: number;
  avg_execution_time: number;
}

const AIAgents: React.FC = () => {
  const [agents, setAgents] = useState<{ [key: string]: AgentStatus }>({});
  const [activity, setActivity] = useState<AgentLog[]>([]);
  const [statistics, setStatistics] = useState<{ [key: string]: AgentStats }>({});
  const [loading, setLoading] = useState(true);
  const [executing, setExecuting] = useState<string | null>(null);

  useEffect(() => {
    fetchAgentData();
    const interval = setInterval(fetchAgentData, 5000); // Refresh every 5 seconds
    return () => clearInterval(interval);
  }, []);

  const fetchAgentData = async () => {
    try {
      // Fetch agent status
      const statusResponse = await axios.get('http://localhost:8000/api/agents/status');
      if (statusResponse.data.success) {
        setAgents(statusResponse.data.status.agents);
      }

      // Fetch activity logs
      const activityResponse = await axios.get('http://localhost:8000/api/agents/activity?limit=20');
      if (activityResponse.data.success) {
        setActivity(activityResponse.data.logs);
      }

      // Fetch statistics
      const statsResponse = await axios.get('http://localhost:8000/api/agents/statistics');
      if (statsResponse.data.success) {
        setStatistics(statsResponse.data.statistics);
      }

      setLoading(false);
    } catch (error) {
      console.error('Error fetching agent data:', error);
      setLoading(false);
    }
  };

  const executeRouteOptimizer = async () => {
    setExecuting('route_optimizer');
    try {
      // Get sample data from database
      const ordersResponse = await axios.get('http://localhost:8000/api/data-preview?type=orders&limit=20');
      const orders = ordersResponse.data.data;

      // Prepare data for agent
      const data = {
        current_routes: [{
          route_id: 1,
          deliveries: orders.slice(0, 10).map((order: any, idx: number) => ({
            id: order.id,
            lat: order.latitude,
            lon: order.longitude,
            priority: idx < 2 ? 'urgent' : 'normal'
          })),
          efficiency: 0.65
        }],
        traffic_data: {
          congestion_level: Math.random() > 0.5 ? 'high' : 'medium'
        }
      };

      const response = await axios.post('http://localhost:8000/api/agents/route-optimizer/execute', data);

      if (response.data.success) {
        alert('✅ Route optimization complete! Check activity logs below.');
        fetchAgentData();
      }
    } catch (error: any) {
      alert('❌ Error: ' + (error.response?.data?.error || error.message));
    } finally {
      setExecuting(null);
    }
  };

  const executeDemandPredictor = async () => {
    setExecuting('demand_predictor');
    try {
      // Get historical orders
      const ordersResponse = await axios.get('http://localhost:8000/api/data-preview?type=orders&limit=100');

      // Check if data exists
      if (!ordersResponse.data) {
        throw new Error('No response data from API');
      }

      const orders = ordersResponse.data.data || ordersResponse.data.orders;

      // Validate orders data
      if (!orders || !Array.isArray(orders) || orders.length === 0) {
        throw new Error('No orders data available. Please upload some order data first.');
      }

      const data = {
        historical_orders: orders,
        current_capacity: {
          vehicles: 10,
          drivers: 10,
          deliveries_per_vehicle: 30
        },
        external_factors: {
          weather: { condition: 'clear' },
          events: [],
          holidays: []
        }
      };

      const response = await axios.post('http://localhost:8000/api/agents/demand-predictor/execute', data);

      if (response.data.success) {
        alert('✅ Demand forecasting complete! Check activity logs below.');
        fetchAgentData();
      }
    } catch (error: any) {
      alert('❌ Error: ' + (error.response?.data?.error || error.message));
    } finally {
      setExecuting(null);
    }
  };

  const simulateScenario = async (scenario: string) => {
    setExecuting('orchestrator');
    try {
      const response = await axios.post('http://localhost:8000/api/agents/simulate', {
        scenario: scenario,
        parameters: {}
      });

      if (response.data.success) {
        alert(`✅ ${scenario} scenario simulation complete!`);
        fetchAgentData();
      }
    } catch (error: any) {
      alert('❌ Error: ' + (error.response?.data?.error || error.message));
    } finally {
      setExecuting(null);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-2">
            <Bot className="h-8 w-8 text-blue-600" />
            AI Agents Dashboard
          </h1>
          <p className="text-gray-600 mt-1">Monitor and control autonomous AI agents</p>
        </div>
      </div>

      {/* GenAI Comparison Banner */}
      <div className="bg-gradient-to-r from-purple-50 to-blue-50 border-2 border-purple-200 rounded-lg p-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Sparkles className="h-6 w-6 text-purple-600" />
            <div>
              <h3 className="font-semibold text-gray-900">New: GenAI-Powered Agents Available!</h3>
              <p className="text-sm text-gray-600">Compare traditional vs Azure OpenAI-powered agents with natural language explanations</p>
            </div>
          </div>
          <Link
            to="/agent-comparison"
            className="flex items-center gap-2 bg-purple-600 text-white px-4 py-2 rounded-lg hover:bg-purple-700 transition-colors font-medium"
          >
            Compare Agents
            <ArrowRight className="h-4 w-4" />
          </Link>
        </div>
      </div>

      {/* Agent Status Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {Object.entries(agents).map(([agentKey, agent]) => (
          <div key={agentKey} className="bg-white rounded-lg shadow-md p-6">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-3">
                {agentKey === 'route_optimizer' ? (
                  <Route className="h-8 w-8 text-blue-600" />
                ) : agentKey === 'demand_predictor' ? (
                  <TrendingUp className="h-8 w-8 text-green-600" />
                ) : (
                  <Brain className="h-8 w-8 text-purple-600" />
                )}
                <div>
                  <h3 className="font-semibold text-gray-900">{agent.name}</h3>
                  <p className="text-sm text-gray-500">{agent.agent_id}</p>
                </div>
              </div>
              <span className={`px-3 py-1 rounded-full text-sm font-medium ${
                agent.status === 'idle' ? 'bg-green-100 text-green-800' :
                agent.status === 'active' ? 'bg-blue-100 text-blue-800' :
                'bg-red-100 text-red-800'
              }`}>
                {agent.status}
              </span>
            </div>

            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span className="text-gray-600">Success Rate</span>
                <span className="font-semibold text-gray-900">
                  {(agent.metrics.success_rate * 100).toFixed(1)}%
                </span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-gray-600">Tasks Completed</span>
                <span className="font-semibold text-gray-900">
                  {agent.metrics.tasks_completed}
                </span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-gray-600">Avg Execution</span>
                <span className="font-semibold text-gray-900">
                  {agent.metrics.average_execution_time.toFixed(2)}s
                </span>
              </div>
            </div>

            <div className="mt-4 pt-4 border-t">
              <p className="text-xs text-gray-500 mb-2">Capabilities:</p>
              <div className="flex flex-wrap gap-1">
                {agent.capabilities.slice(0, 3).map((cap, idx) => (
                  <span key={idx} className="text-xs bg-gray-100 text-gray-700 px-2 py-1 rounded">
                    {cap}
                  </span>
                ))}
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Action Buttons */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <h2 className="text-xl font-bold text-gray-900 mb-4 flex items-center gap-2">
          <Zap className="h-5 w-5 text-yellow-600" />
          Execute Agent Actions
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <button
            onClick={executeRouteOptimizer}
            disabled={executing !== null}
            className="bg-blue-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors flex items-center justify-center gap-2"
          >
            {executing === 'route_optimizer' ? (
              <>
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                Optimizing...
              </>
            ) : (
              <>
                <Route className="h-5 w-5" />
                Optimize Routes
              </>
            )}
          </button>

          <button
            onClick={executeDemandPredictor}
            disabled={executing !== null}
            className="bg-green-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-green-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors flex items-center justify-center gap-2"
          >
            {executing === 'demand_predictor' ? (
              <>
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                Forecasting...
              </>
            ) : (
              <>
                <TrendingUp className="h-5 w-5" />
                Forecast Demand
              </>
            )}
          </button>

          <button
            onClick={() => simulateScenario('high_demand')}
            disabled={executing !== null}
            className="bg-purple-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-purple-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors flex items-center justify-center gap-2"
          >
            {executing === 'orchestrator' ? (
              <>
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                Simulating...
              </>
            ) : (
              <>
                <Brain className="h-5 w-5" />
                Simulate Scenario
              </>
            )}
          </button>
        </div>
      </div>

      {/* Statistics */}
      {Object.keys(statistics).length > 0 && (
        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-xl font-bold text-gray-900 mb-4">Performance Statistics</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {Object.entries(statistics).map(([agentName, stats]) => (
              <div key={agentName} className="border rounded-lg p-4">
                <h3 className="font-semibold text-gray-900 mb-3">{agentName}</h3>
                <div className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-600">Total Actions</span>
                    <span className="font-semibold">{stats.total_actions}</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-600">Success Rate</span>
                    <span className="font-semibold text-green-600">{stats.success_rate}%</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-600">Avg Time</span>
                    <span className="font-semibold">{stats.avg_execution_time}s</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Recent Activity */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <h2 className="text-xl font-bold text-gray-900 mb-4 flex items-center gap-2">
          <Activity className="h-5 w-5 text-blue-600" />
          Recent Agent Activity
        </h2>
        <div className="space-y-3">
          {activity.length === 0 ? (
            <p className="text-gray-500 text-center py-8">No agent activity yet. Execute an action above to see logs.</p>
          ) : (
            activity.map((log, idx) => (
              <div key={idx} className="border rounded-lg p-4 hover:bg-gray-50 transition-colors">
                <div className="flex items-start justify-between">
                  <div className="flex items-start gap-3 flex-1">
                    {log.success ? (
                      <CheckCircle className="h-5 w-5 text-green-600 mt-0.5" />
                    ) : (
                      <XCircle className="h-5 w-5 text-red-600 mt-0.5" />
                    )}
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-1">
                        <span className="font-semibold text-gray-900">{log.agent_name}</span>
                        <span className="text-xs text-gray-500">•</span>
                        <span className="text-sm text-gray-600">{log.action}</span>
                      </div>
                      <div className="flex items-center gap-4 text-xs text-gray-500">
                        <span className="flex items-center gap-1">
                          <Clock className="h-3 w-3" />
                          {log.execution_time?.toFixed(2) || 0}s
                        </span>
                        <span>{new Date(log.timestamp).toLocaleString()}</span>
                      </div>
                    </div>
                  </div>
                  <span className={`px-2 py-1 rounded text-xs font-medium ${
                    log.success ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                  }`}>
                    {log.success ? 'Success' : 'Failed'}
                  </span>
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
};

export default AIAgents;


