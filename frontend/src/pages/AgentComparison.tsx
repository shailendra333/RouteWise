import React, { useState, useEffect } from 'react';
import { Bot, Brain, Zap, TrendingUp, Route, MessageSquare, FileText, BarChart3, Clock, DollarSign, CheckCircle, XCircle, Sparkles } from 'lucide-react';
import axios from 'axios';
import AgentThinkingStream from '../components/AgentThinkingStream';

interface ComparisonData {
  traditional_agents: any;
  genai_agents: any;
  comparison_matrix: any;
}

const AgentComparison: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'overview' | 'traditional' | 'genai' | 'sidebyside'>('overview');
  const [comparisonData, setComparisonData] = useState<ComparisonData | null>(null);
  const [traditionalStatus, setTraditionalStatus] = useState<any>(null);
  const [genaiStatus, setGenaiStatus] = useState<any>(null);
  const [executing, setExecuting] = useState<string | null>(null);
  const [chatMessage, setChatMessage] = useState('');
  const [chatResponse, setChatResponse] = useState('');
  const [loading, setLoading] = useState(true);
  const [tradRunId, setTradRunId] = useState<string | null>(null);
  const [genaiRunId, setGenaiRunId] = useState<string | null>(null);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      // Fetch comparison data
      const compResponse = await axios.get('http://localhost:8000/api/genai-agents/compare');
      setComparisonData(compResponse.data);

      // Fetch traditional agent status
      try {
        const tradResponse = await axios.get('http://localhost:8000/api/agents/status');
        if (tradResponse.data.success) {
          setTraditionalStatus(tradResponse.data.status);
        }
      } catch (error) {
        console.error('Traditional agents not available:', error);
      }

      // Fetch GenAI agent status
      try {
        const genaiResponse = await axios.get('http://localhost:8000/api/genai-agents/status');
        if (genaiResponse.data.success) {
          setGenaiStatus(genaiResponse.data.status);
        }
      } catch (error) {
        console.error('GenAI agents not available:', error);
      }

      setLoading(false);
    } catch (error) {
      console.error('Error fetching comparison data:', error);
      setLoading(false);
    }
  };

  const executeAgent = async (type: 'traditional' | 'genai', agent: 'route' | 'demand') => {
    setExecuting(`${type}-${agent}`);
    try {
      const ordersResponse = await axios.get('http://localhost:8000/api/data-preview?type=orders&limit=20');

      // Check if data exists
      if (!ordersResponse.data) {
        throw new Error('No response data from API');
      }

      const orders = ordersResponse.data.data || ordersResponse.data.orders;

      // Validate orders data
      if (!orders || !Array.isArray(orders) || orders.length === 0) {
        throw new Error('No orders data available. Please upload some order data first.');
      }

      const data = agent === 'route' ? {
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
        traffic_data: { congestion_level: 'high' }
      } : {
        historical_orders: orders,
        current_capacity: { vehicles: 10, drivers: 10 },
        external_factors: { weather: { condition: 'clear' } }
      };

      const endpoint = type === 'traditional'
        ? `/api/agents/${agent === 'route' ? 'route-optimizer' : 'demand-predictor'}/execute`
        : `/api/genai-agents/${agent === 'route' ? 'route-optimizer' : 'demand-predictor'}/execute`;

      const startTime = Date.now();
      const response = await axios.post(`http://localhost:8000${endpoint}`, data);
      const endTime = Date.now();
      const executionTime = ((endTime - startTime) / 1000).toFixed(2);

      if (response.data.success) {
        const explanation = response.data.natural_explanation || response.data.result?.natural_explanation || 'Task completed successfully';
        alert(`✅ ${type === 'traditional' ? 'Traditional' : 'GenAI'} Agent\n\nExecution Time: ${executionTime}s\n\n${explanation}`);
      }
    } catch (error: any) {
      alert(`❌ Error: ${error.response?.data?.error || error.message}`);
    } finally {
      setExecuting(null);
    }
  };

  // Starts a traced (streamable) execution and stores the run_id so the
  // AgentThinkingStream component can poll and render live reasoning.
  const executeAgentTraced = async (type: 'traditional' | 'genai', agent: 'route' | 'demand') => {
    const key = `${type}-${agent}`;
    setExecuting(key);
    if (type === 'traditional') setTradRunId(null); else setGenaiRunId(null);

    try {
      const ordersResponse = await axios.get('http://localhost:8000/api/data-preview?type=orders&limit=20');
      const orders = ordersResponse.data?.data || ordersResponse.data?.orders;

      if (!orders || !Array.isArray(orders) || orders.length === 0) {
        throw new Error('No orders data available. Please upload some order data first.');
      }

      const data = agent === 'route' ? {
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
        traffic_data: { congestion_level: 'high' }
      } : {
        historical_orders: orders,
        current_capacity: { vehicles: 10, drivers: 10 },
        external_factors: { weather: { condition: 'clear' } }
      };

      const endpoint = type === 'traditional'
        ? `/api/agents/${agent === 'route' ? 'route-optimizer' : 'demand-predictor'}/execute-traced`
        : `/api/genai-agents/${agent === 'route' ? 'route-optimizer' : 'demand-predictor'}/execute-traced`;

      const response = await axios.post(`http://localhost:8000${endpoint}`, data);

      if (response.data.success) {
        if (type === 'traditional') setTradRunId(response.data.run_id);
        else setGenaiRunId(response.data.run_id);
      }
    } catch (error: any) {
      alert(`❌ Error: ${error.response?.data?.error || error.message}`);
    } finally {
      setExecuting(null);
    }
  };

  const handleChat = async () => {
    if (!chatMessage.trim()) return;

    setExecuting('chat');
    try {
      const response = await axios.post('http://localhost:8000/api/genai-agents/chat', {
        message: chatMessage
      });

      if (response.data.success) {
        setChatResponse(response.data.response);
      }
    } catch (error: any) {
      setChatResponse(`Error: ${error.response?.data?.error || error.message}`);
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
            <BarChart3 className="h-8 w-8 text-blue-600" />
            Agent Comparison Dashboard
          </h1>
          <p className="text-gray-600 mt-1">Compare Traditional vs GenAI-Powered Agents</p>
        </div>
      </div>

      {/* Tabs */}
      <div className="bg-white rounded-lg shadow-md">
        <div className="border-b border-gray-200">
          <nav className="flex -mb-px">
            <button
              onClick={() => setActiveTab('overview')}
              className={`px-6 py-3 font-medium text-sm border-b-2 transition-colors ${
                activeTab === 'overview'
                  ? 'border-blue-600 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              Overview
            </button>
            <button
              onClick={() => setActiveTab('traditional')}
              className={`px-6 py-3 font-medium text-sm border-b-2 transition-colors ${
                activeTab === 'traditional'
                  ? 'border-blue-600 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              <Bot className="h-4 w-4 inline mr-2" />
              Traditional Agents
            </button>
            <button
              onClick={() => setActiveTab('genai')}
              className={`px-6 py-3 font-medium text-sm border-b-2 transition-colors ${
                activeTab === 'genai'
                  ? 'border-purple-600 text-purple-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              <Sparkles className="h-4 w-4 inline mr-2" />
              GenAI Agents
            </button>
            <button
              onClick={() => setActiveTab('sidebyside')}
              className={`px-6 py-3 font-medium text-sm border-b-2 transition-colors ${
                activeTab === 'sidebyside'
                  ? 'border-green-600 text-green-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              Side-by-Side Test
            </button>
          </nav>
        </div>

        <div className="p-6">
          {/* Overview Tab */}
          {activeTab === 'overview' && comparisonData && (
            <div className="space-y-6">
              {/* Feature Comparison Matrix */}
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Traditional Agents */}
                <div className="border-2 border-blue-200 rounded-lg p-6 bg-blue-50">
                  <div className="flex items-center gap-3 mb-4">
                    <Bot className="h-8 w-8 text-blue-600" />
                    <div>
                      <h3 className="text-xl font-bold text-gray-900">Traditional Agents</h3>
                      <p className="text-sm text-gray-600">{comparisonData.traditional_agents.type}</p>
                    </div>
                  </div>

                  <div className="space-y-3">
                    <div className="bg-white rounded p-3">
                      <p className="text-sm text-gray-600">Decision Making</p>
                      <p className="font-semibold text-gray-900">{comparisonData.traditional_agents.decision_making}</p>
                    </div>
                    <div className="bg-white rounded p-3">
                      <p className="text-sm text-gray-600">Explanation</p>
                      <p className="font-semibold text-gray-900">{comparisonData.traditional_agents.explanation}</p>
                    </div>
                    <div className="bg-white rounded p-3">
                      <p className="text-sm text-gray-600">Interaction</p>
                      <p className="font-semibold text-gray-900">{comparisonData.traditional_agents.interaction}</p>
                    </div>
                  </div>

                  <div className="mt-4">
                    <p className="text-sm font-semibold text-gray-700 mb-2">Strengths:</p>
                    <ul className="space-y-1">
                      {comparisonData.traditional_agents.strengths.map((strength: string, idx: number) => (
                        <li key={idx} className="flex items-start gap-2 text-sm">
                          <CheckCircle className="h-4 w-4 text-green-600 mt-0.5 flex-shrink-0" />
                          <span className="text-gray-700">{strength}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                </div>

                {/* GenAI Agents */}
                <div className="border-2 border-purple-200 rounded-lg p-6 bg-purple-50">
                  <div className="flex items-center gap-3 mb-4">
                    <Sparkles className="h-8 w-8 text-purple-600" />
                    <div>
                      <h3 className="text-xl font-bold text-gray-900">GenAI Agents</h3>
                      <p className="text-sm text-gray-600">{comparisonData.genai_agents.type}</p>
                    </div>
                  </div>

                  <div className="space-y-3">
                    <div className="bg-white rounded p-3">
                      <p className="text-sm text-gray-600">Decision Making</p>
                      <p className="font-semibold text-gray-900">{comparisonData.genai_agents.decision_making}</p>
                    </div>
                    <div className="bg-white rounded p-3">
                      <p className="text-sm text-gray-600">Explanation</p>
                      <p className="font-semibold text-gray-900">{comparisonData.genai_agents.explanation}</p>
                    </div>
                    <div className="bg-white rounded p-3">
                      <p className="text-sm text-gray-600">Interaction</p>
                      <p className="font-semibold text-gray-900">{comparisonData.genai_agents.interaction}</p>
                    </div>
                  </div>

                  <div className="mt-4">
                    <p className="text-sm font-semibold text-gray-700 mb-2">Strengths:</p>
                    <ul className="space-y-1">
                      {comparisonData.genai_agents.strengths.map((strength: string, idx: number) => (
                        <li key={idx} className="flex items-start gap-2 text-sm">
                          <CheckCircle className="h-4 w-4 text-green-600 mt-0.5 flex-shrink-0" />
                          <span className="text-gray-700">{strength}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                </div>
              </div>

              {/* Comparison Matrix */}
              <div className="bg-white rounded-lg border p-6">
                <h3 className="text-lg font-bold text-gray-900 mb-4">Performance Comparison</h3>
                <div className="overflow-x-auto">
                  <table className="min-w-full divide-y divide-gray-200">
                    <thead>
                      <tr>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Metric
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Traditional
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          GenAI
                        </th>
                      </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-gray-200">
                      {Object.entries(comparisonData.comparison_matrix).map(([key, values]: [string, any]) => (
                        <tr key={key}>
                          <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900 capitalize">
                            {key.replace(/_/g, ' ')}
                          </td>
                          <td className="px-6 py-4 text-sm text-gray-700">{values.traditional}</td>
                          <td className="px-6 py-4 text-sm text-gray-700">{values.genai}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>

              {/* Recommendation */}
              <div className="bg-gradient-to-r from-blue-50 to-purple-50 rounded-lg p-6 border-2 border-blue-200">
                <div className="flex items-start gap-3">
                  <Zap className="h-6 w-6 text-yellow-600 mt-1" />
                  <div>
                    <h3 className="text-lg font-bold text-gray-900 mb-2">Recommendation</h3>
                    <p className="text-gray-700">{comparisonData.recommendation}</p>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Traditional Agents Tab */}
          {activeTab === 'traditional' && (
            <div className="space-y-6">
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
                <h3 className="text-lg font-bold text-gray-900 mb-4 flex items-center gap-2">
                  <Bot className="h-6 w-6 text-blue-600" />
                  Traditional Agent Status
                </h3>
                {traditionalStatus ? (
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    {Object.entries(traditionalStatus.agents || {}).map(([key, agent]: [string, any]) => (
                      <div key={key} className="bg-white rounded-lg p-4 shadow">
                        <h4 className="font-semibold text-gray-900 mb-2">{agent.name}</h4>
                        <div className="space-y-1 text-sm">
                          <p><span className="text-gray-600">Status:</span> <span className="font-medium">{agent.status}</span></p>
                          <p><span className="text-gray-600">Success Rate:</span> <span className="font-medium">{(agent.metrics.success_rate * 100).toFixed(1)}%</span></p>
                          <p><span className="text-gray-600">Tasks:</span> <span className="font-medium">{agent.metrics.tasks_completed}</span></p>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-gray-600">Traditional agents not available. Make sure backend is running.</p>
                )}
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <button
                  onClick={() => executeAgent('traditional', 'route')}
                  disabled={executing !== null}
                  className="bg-blue-600 text-white p-6 rounded-lg font-medium hover:bg-blue-700 disabled:bg-gray-400 transition-colors"
                >
                  <Route className="h-8 w-8 mx-auto mb-2" />
                  {executing === 'traditional-route' ? 'Executing...' : 'Test Route Optimizer'}
                </button>
                <button
                  onClick={() => executeAgent('traditional', 'demand')}
                  disabled={executing !== null}
                  className="bg-blue-600 text-white p-6 rounded-lg font-medium hover:bg-blue-700 disabled:bg-gray-400 transition-colors"
                >
                  <TrendingUp className="h-8 w-8 mx-auto mb-2" />
                  {executing === 'traditional-demand' ? 'Executing...' : 'Test Demand Predictor'}
                </button>
              </div>
            </div>
          )}

          {/* GenAI Agents Tab */}
          {activeTab === 'genai' && (
            <div className="space-y-6">
              <div className="bg-purple-50 border border-purple-200 rounded-lg p-6">
                <h3 className="text-lg font-bold text-gray-900 mb-4 flex items-center gap-2">
                  <Sparkles className="h-6 w-6 text-purple-600" />
                  GenAI Agent Status
                </h3>
                {genaiStatus ? (
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    {Object.entries(genaiStatus.agents || {}).map(([key, agent]: [string, any]) => (
                      <div key={key} className="bg-white rounded-lg p-4 shadow">
                        <h4 className="font-semibold text-gray-900 mb-2">{agent.name}</h4>
                        <div className="space-y-1 text-sm">
                          <p><span className="text-gray-600">Status:</span> <span className="font-medium">{agent.status}</span></p>
                          <p><span className="text-gray-600">GenAI:</span> <span className="font-medium text-purple-600">Azure OpenAI</span></p>
                          <p><span className="text-gray-600">Model:</span> <span className="font-medium">GPT-4</span></p>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="bg-yellow-50 border border-yellow-200 rounded p-4">
                    <p className="text-yellow-800">⚠️ GenAI agents not available. Configure Azure OpenAI credentials in backend/.env</p>
                  </div>
                )}
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <button
                  onClick={() => executeAgent('genai', 'route')}
                  disabled={executing !== null || !genaiStatus}
                  className="bg-purple-600 text-white p-6 rounded-lg font-medium hover:bg-purple-700 disabled:bg-gray-400 transition-colors"
                >
                  <Route className="h-8 w-8 mx-auto mb-2" />
                  {executing === 'genai-route' ? 'Executing...' : 'Test GenAI Route Optimizer'}
                </button>
                <button
                  onClick={() => executeAgent('genai', 'demand')}
                  disabled={executing !== null || !genaiStatus}
                  className="bg-purple-600 text-white p-6 rounded-lg font-medium hover:bg-purple-700 disabled:bg-gray-400 transition-colors"
                >
                  <TrendingUp className="h-8 w-8 mx-auto mb-2" />
                  {executing === 'genai-demand' ? 'Executing...' : 'Test GenAI Demand Predictor'}
                </button>
              </div>

              {/* Chat Interface */}
              {genaiStatus && (
                <div className="bg-white border rounded-lg p-6">
                  <h3 className="text-lg font-bold text-gray-900 mb-4 flex items-center gap-2">
                    <MessageSquare className="h-6 w-6 text-purple-600" />
                    Chat with GenAI Agents
                  </h3>
                  <div className="space-y-4">
                    <div className="flex gap-3">
                      <input
                        type="text"
                        value={chatMessage}
                        onChange={(e) => setChatMessage(e.target.value)}
                        onKeyPress={(e) => e.key === 'Enter' && handleChat()}
                        placeholder="Ask a question... (e.g., 'How many deliveries were completed today?')"
                        className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                      />
                      <button
                        onClick={handleChat}
                        disabled={executing === 'chat' || !chatMessage.trim()}
                        className="bg-purple-600 text-white px-6 py-2 rounded-lg font-medium hover:bg-purple-700 disabled:bg-gray-400 transition-colors"
                      >
                        {executing === 'chat' ? 'Sending...' : 'Send'}
                      </button>
                    </div>
                    {chatResponse && (
                      <div className="bg-purple-50 border border-purple-200 rounded-lg p-4">
                        <p className="text-sm text-gray-700">{chatResponse}</p>
                      </div>
                    )}
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Side-by-Side Test Tab */}
          {activeTab === 'sidebyside' && (
            <div className="space-y-6">
              <div className="bg-gradient-to-r from-blue-50 to-purple-50 rounded-lg p-6 border">
                <h3 className="text-lg font-bold text-gray-900 mb-2">Side-by-Side Performance Test</h3>
                <p className="text-gray-600 text-sm">Execute the same task on both agent systems to compare performance, speed, and explanation quality.</p>
              </div>

              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Traditional Side */}
                <div className="border-2 border-blue-200 rounded-lg p-6 bg-blue-50">
                  <div className="flex items-center gap-3 mb-4">
                    <Bot className="h-6 w-6 text-blue-600" />
                    <h3 className="text-lg font-bold text-gray-900">Traditional Agent</h3>
                  </div>
                  <div className="space-y-3">
                    <button
                      onClick={() => executeAgentTraced('traditional', 'route')}
                      disabled={executing !== null}
                      className="w-full bg-blue-600 text-white p-4 rounded-lg font-medium hover:bg-blue-700 disabled:bg-gray-400 transition-colors flex items-center justify-center gap-2"
                    >
                      <Route className="h-5 w-5" />
                      {executing === 'traditional-route' ? 'Starting...' : 'Execute Route Optimization'}
                    </button>
                    <button
                      onClick={() => executeAgentTraced('traditional', 'demand')}
                      disabled={executing !== null}
                      className="w-full bg-blue-600 text-white p-4 rounded-lg font-medium hover:bg-blue-700 disabled:bg-gray-400 transition-colors flex items-center justify-center gap-2"
                    >
                      <TrendingUp className="h-5 w-5" />
                      {executing === 'traditional-demand' ? 'Starting...' : 'Execute Demand Forecasting'}
                    </button>
                  </div>
                  <div className="mt-4 p-3 bg-white rounded text-sm">
                    <p className="text-gray-600 mb-1">Expected:</p>
                    <ul className="space-y-1 text-xs text-gray-700">
                      <li>⚡ Response time: &lt;100ms</li>
                      <li>💰 Cost: $0</li>
                      <li>📝 Output: Technical metrics</li>
                    </ul>
                  </div>
                  {tradRunId && (
                    <div className="mt-4">
                      <AgentThinkingStream runId={tradRunId} theme="blue" />
                    </div>
                  )}
                </div>

                {/* GenAI Side */}
                <div className="border-2 border-purple-200 rounded-lg p-6 bg-purple-50">
                  <div className="flex items-center gap-3 mb-4">
                    <Sparkles className="h-6 w-6 text-purple-600" />
                    <h3 className="text-lg font-bold text-gray-900">GenAI Agent</h3>
                  </div>
                  <div className="space-y-3">
                    <button
                      onClick={() => executeAgentTraced('genai', 'route')}
                      disabled={executing !== null || !genaiStatus}
                      className="w-full bg-purple-600 text-white p-4 rounded-lg font-medium hover:bg-purple-700 disabled:bg-gray-400 transition-colors flex items-center justify-center gap-2"
                    >
                      <Route className="h-5 w-5" />
                      {executing === 'genai-route' ? 'Starting...' : 'Execute Route Optimization'}
                    </button>
                    <button
                      onClick={() => executeAgentTraced('genai', 'demand')}
                      disabled={executing !== null || !genaiStatus}
                      className="w-full bg-purple-600 text-white p-4 rounded-lg font-medium hover:bg-purple-700 disabled:bg-gray-400 transition-colors flex items-center justify-center gap-2"
                    >
                      <TrendingUp className="h-5 w-5" />
                      {executing === 'genai-demand' ? 'Starting...' : 'Execute Demand Forecasting'}
                    </button>
                  </div>
                  <div className="mt-4 p-3 bg-white rounded text-sm">
                    <p className="text-gray-600 mb-1">Expected:</p>
                    <ul className="space-y-1 text-xs text-gray-700">
                      <li>⏱️ Response time: 1-3s</li>
                      <li>💳 Cost: ~$0.03-0.06</li>
                      <li>📖 Output: Natural language + metrics</li>
                    </ul>
                  </div>
                  {genaiRunId && (
                    <div className="mt-4">
                      <AgentThinkingStream runId={genaiRunId} theme="purple" />
                    </div>
                  )}
                </div>
              </div>

              {/* Instructions */}
              <div className="bg-white border rounded-lg p-6">
                <h4 className="font-bold text-gray-900 mb-3">How to Compare:</h4>
                <ol className="list-decimal list-inside space-y-2 text-sm text-gray-700">
                  <li>Click the same action button on both sides (e.g., "Execute Route Optimization")</li>
                  <li>Watch each agent's live Perceive → Decide → Act → Learn reasoning stream appear in real time</li>
                  <li>Compare the explanation quality (Traditional = technical, GenAI = natural language from GPT-4)</li>
                  <li>Evaluate which approach better suits your use case</li>
                </ol>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default AgentComparison;


