import React, { useState, useEffect } from 'react';
import { Brain, TrendingUp, Target, Lightbulb, Activity } from 'lucide-react';

interface LearningStats {
  total_decisions: number;
  decisions_with_outcomes: number;
  avg_decision_quality: number;
  prediction_accuracy: number;
  total_patterns: number;
  high_confidence_patterns: number;
  avg_time_savings: number;
  avg_cost_savings: number;
  recent_quality_score: number;
  quality_improvement: number;
}

interface LearnedPattern {
  pattern_type: string;
  conditions: any;
  confidence: number;
  observations: number;
  success_rate: number;
  avg_improvement_minutes: number;
  description: string;
}

interface LearningInsights {
  statistics: LearningStats;
  top_patterns: LearnedPattern[];
  learning_status: string;
}

const SelfLearningDashboard: React.FC = () => {
  const [insights, setInsights] = useState<LearningInsights | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchLearningInsights();
    // Refresh every 30 seconds
    const interval = setInterval(fetchLearningInsights, 30000);
    return () => clearInterval(interval);
  }, []);

  const fetchLearningInsights = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/genai-agents/route-optimizer/learning-insights');
      const data = await response.json();

      if (data.success) {
        setInsights(data.insights);
        setError(null);
      } else {
        setError('Failed to fetch learning insights');
      }
    } catch (err) {
      setError('Error connecting to backend');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const simulateOutcome = async (success: boolean) => {
    try {
      await fetch('http://localhost:8000/api/genai-agents/learning/simulate-outcome', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ success })
      });

      // Refresh insights after simulation
      setTimeout(fetchLearningInsights, 1000);
    } catch (err) {
      console.error('Error simulating outcome:', err);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-8 bg-red-50 border border-red-200 rounded-lg">
        <p className="text-red-700">⚠️ {error}</p>
      </div>
    );
  }

  if (!insights) return null;

  const stats = insights.statistics;
  const patterns = insights.top_patterns || [];

  return (
    <div className="space-y-6 p-6 bg-gradient-to-br from-blue-50 to-indigo-50">
      {/* Header */}
      <div className="bg-white rounded-xl shadow-lg p-6 border-l-4 border-indigo-500">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="bg-indigo-100 p-3 rounded-lg">
              <Brain className="h-8 w-8 text-indigo-600" />
            </div>
            <div>
              <h2 className="text-2xl font-bold text-gray-800">Self-Learning Route Optimizer</h2>
              <p className="text-gray-600">AI that learns from every decision</p>
            </div>
          </div>
          <div className="flex items-center space-x-2">
            <span className={`px-3 py-1 rounded-full text-sm font-medium ${
              insights.learning_status === 'active'
                ? 'bg-green-100 text-green-700'
                : 'bg-yellow-100 text-yellow-700'
            }`}>
              {insights.learning_status === 'active' ? '🟢 Learning Active' : '🟡 Initializing'}
            </span>
          </div>
        </div>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Prediction Accuracy */}
        <div className="bg-white rounded-lg shadow-md p-5 hover:shadow-lg transition-shadow">
          <div className="flex items-start justify-between">
            <div>
              <p className="text-sm text-gray-600 font-medium">Prediction Accuracy</p>
              <p className="text-3xl font-bold text-indigo-600 mt-2">
                {(stats.prediction_accuracy * 100).toFixed(1)}%
              </p>
              {stats.prediction_accuracy >= 0.85 && (
                <p className="text-xs text-green-600 mt-1">✓ Excellent performance</p>
              )}
            </div>
            <Target className="h-8 w-8 text-indigo-300" />
          </div>
        </div>

        {/* Decision Quality */}
        <div className="bg-white rounded-lg shadow-md p-5 hover:shadow-lg transition-shadow">
          <div className="flex items-start justify-between">
            <div>
              <p className="text-sm text-gray-600 font-medium">Avg Decision Quality</p>
              <p className="text-3xl font-bold text-green-600 mt-2">
                {(stats.avg_decision_quality * 100).toFixed(0)}%
              </p>
              {stats.quality_improvement > 0 && (
                <p className="text-xs text-green-600 mt-1 flex items-center">
                  <TrendingUp className="h-3 w-3 mr-1" />
                  +{stats.quality_improvement.toFixed(1)}% improved
                </p>
              )}
            </div>
            <Activity className="h-8 w-8 text-green-300" />
          </div>
        </div>

        {/* Patterns Learned */}
        <div className="bg-white rounded-lg shadow-md p-5 hover:shadow-lg transition-shadow">
          <div className="flex items-start justify-between">
            <div>
              <p className="text-sm text-gray-600 font-medium">Patterns Learned</p>
              <p className="text-3xl font-bold text-purple-600 mt-2">
                {stats.total_patterns}
              </p>
              <p className="text-xs text-purple-600 mt-1">
                {stats.high_confidence_patterns} high confidence
              </p>
            </div>
            <Lightbulb className="h-8 w-8 text-purple-300" />
          </div>
        </div>

        {/* Total Savings */}
        <div className="bg-white rounded-lg shadow-md p-5 hover:shadow-lg transition-shadow">
          <div className="flex items-start justify-between">
            <div>
              <p className="text-sm text-gray-600 font-medium">Avg Time Savings</p>
              <p className="text-3xl font-bold text-orange-600 mt-2">
                {stats.avg_time_savings.toFixed(0)}<span className="text-lg">min</span>
              </p>
              <p className="text-xs text-orange-600 mt-1">
                ${stats.avg_cost_savings.toFixed(2)} cost savings
              </p>
            </div>
            <TrendingUp className="h-8 w-8 text-orange-300" />
          </div>
        </div>
      </div>

      {/* Learning Progress Bar */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <h3 className="text-lg font-semibold text-gray-800 mb-4">Learning Progress</h3>
        <div className="space-y-3">
          <div>
            <div className="flex justify-between text-sm mb-1">
              <span className="text-gray-600">Decisions Analyzed</span>
              <span className="font-medium text-gray-800">
                {stats.decisions_with_outcomes} / {stats.total_decisions}
              </span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2.5">
              <div
                className="bg-indigo-600 h-2.5 rounded-full transition-all duration-500"
                style={{
                  width: `${(stats.decisions_with_outcomes / Math.max(stats.total_decisions, 1)) * 100}%`
                }}
              ></div>
            </div>
          </div>

          <div>
            <div className="flex justify-between text-sm mb-1">
              <span className="text-gray-600">Prediction Accuracy</span>
              <span className="font-medium text-gray-800">
                {(stats.prediction_accuracy * 100).toFixed(1)}%
              </span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2.5">
              <div
                className={`h-2.5 rounded-full transition-all duration-500 ${
                  stats.prediction_accuracy >= 0.85 ? 'bg-green-500' :
                  stats.prediction_accuracy >= 0.7 ? 'bg-yellow-500' : 'bg-red-500'
                }`}
                style={{ width: `${stats.prediction_accuracy * 100}%` }}
              ></div>
            </div>
          </div>

          <div>
            <div className="flex justify-between text-sm mb-1">
              <span className="text-gray-600">Decision Quality Score</span>
              <span className="font-medium text-gray-800">
                {(stats.recent_quality_score * 100).toFixed(0)}%
              </span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2.5">
              <div
                className="bg-purple-600 h-2.5 rounded-full transition-all duration-500"
                style={{ width: `${stats.recent_quality_score * 100}%` }}
              ></div>
            </div>
          </div>
        </div>
      </div>

      {/* Learned Patterns */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-gray-800">Top Learned Patterns</h3>
          <span className="text-sm text-gray-500">{patterns.length} patterns discovered</span>
        </div>

        {patterns.length === 0 ? (
          <div className="text-center py-8 text-gray-500">
            <Lightbulb className="h-12 w-12 mx-auto mb-3 text-gray-300" />
            <p>No patterns learned yet. Make some decisions to start learning!</p>
          </div>
        ) : (
          <div className="space-y-3">
            {patterns.map((pattern, index) => (
              <div
                key={index}
                className="border border-gray-200 rounded-lg p-4 hover:border-indigo-300 hover:bg-indigo-50 transition-all"
              >
                <div className="flex items-start justify-between mb-2">
                  <div className="flex items-center space-x-2">
                    <span className={`px-2 py-1 rounded text-xs font-medium ${
                      pattern.pattern_type === 'reroute' ? 'bg-blue-100 text-blue-700' :
                      pattern.pattern_type === 'optimize' ? 'bg-green-100 text-green-700' :
                      'bg-purple-100 text-purple-700'
                    }`}>
                      {pattern.pattern_type.toUpperCase()}
                    </span>
                    <span className="text-sm font-semibold text-gray-700">
                      {(pattern.confidence * 100).toFixed(0)}% confidence
                    </span>
                  </div>
                  <div className="text-right">
                    <p className="text-sm font-bold text-indigo-600">
                      +{pattern.avg_improvement_minutes.toFixed(0)} min
                    </p>
                    <p className="text-xs text-gray-500">avg savings</p>
                  </div>
                </div>

                <p className="text-sm text-gray-700 mb-2">{pattern.description}</p>

                <div className="flex items-center justify-between text-xs text-gray-500">
                  <span>Success rate: {(pattern.success_rate * 100).toFixed(0)}%</span>
                  <span>{pattern.observations} observations</span>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Demo Controls */}
      <div className="bg-gradient-to-r from-indigo-500 to-purple-600 rounded-lg shadow-md p-6 text-white">
        <h3 className="text-lg font-semibold mb-3">🎬 Demo Controls</h3>
        <p className="text-sm text-indigo-100 mb-4">
          Simulate route optimization outcomes to see the learning system in action
        </p>
        <div className="flex space-x-3">
          <button
            onClick={() => simulateOutcome(true)}
            className="flex-1 bg-white text-green-600 font-medium py-2 px-4 rounded-lg hover:bg-green-50 transition-colors"
          >
            ✅ Simulate Successful Decision
          </button>
          <button
            onClick={() => simulateOutcome(false)}
            className="flex-1 bg-white text-orange-600 font-medium py-2 px-4 rounded-lg hover:bg-orange-50 transition-colors"
          >
            ⚠️ Simulate Failed Decision
          </button>
        </div>
      </div>

      {/* Learning Insights */}
      {stats.quality_improvement !== 0 && (
        <div className="bg-gradient-to-r from-green-50 to-emerald-50 border-l-4 border-green-500 rounded-lg p-6">
          <div className="flex items-start space-x-3">
            <TrendingUp className="h-6 w-6 text-green-600 mt-1" />
            <div>
              <h4 className="font-semibold text-gray-800 mb-1">🎓 Learning Insight</h4>
              <p className="text-gray-700">
                The AI has improved decision quality by <strong>{stats.quality_improvement.toFixed(1)}%</strong> through
                learning from {stats.decisions_with_outcomes} past decisions. With {stats.total_patterns} patterns
                discovered, the system is getting smarter with each optimization!
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default SelfLearningDashboard;

