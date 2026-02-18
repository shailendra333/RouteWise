import React, { useState, useEffect } from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, LineChart, Line, PieChart, Pie, Cell, ResponsiveContainer } from 'recharts';
import { TrendingUp, DollarSign, Clock, Package, Download, Calendar } from 'lucide-react';
import MetricCard from '../components/MetricCard';
import LoadingSpinner from '../components/LoadingSpinner';

const Analytics: React.FC = () => {
  const [timeRange, setTimeRange] = useState('7d');
  const [isLoading, setIsLoading] = useState(false);
  const [analyticsData, setAnalyticsData] = useState<any>(null);

  useEffect(() => {
    fetchAnalytics();
  }, [timeRange]);

  const fetchAnalytics = async () => {
    setIsLoading(true);
    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      setAnalyticsData({
        summary: {
          totalCostSavings: 125420,
          avgDeliveryTime: 28.5,
          routeEfficiency: 94.2,
          fuelSavings: 18.7
        },
        costAnalysis: [
          { month: 'Jan', beforeOptimization: 45000, afterOptimization: 32000 },
          { month: 'Feb', beforeOptimization: 48000, afterOptimization: 34000 },
          { month: 'Mar', beforeOptimization: 52000, afterOptimization: 36000 },
          { month: 'Apr', beforeOptimization: 49000, afterOptimization: 33000 },
          { month: 'May', beforeOptimization: 53000, afterOptimization: 35000 },
          { month: 'Jun', beforeOptimization: 51000, afterOptimization: 34000 }
        ],
        deliveryPerformance: [
          { day: 'Mon', delivered: 245, onTime: 234, delayed: 11 },
          { day: 'Tue', delivered: 267, onTime: 251, delayed: 16 },
          { day: 'Wed', delivered: 289, onTime: 275, delayed: 14 },
          { day: 'Thu', delivered: 312, onTime: 298, delayed: 14 },
          { day: 'Fri', delivered: 334, onTime: 318, delayed: 16 },
          { day: 'Sat', delivered: 198, onTime: 189, delayed: 9 },
          { day: 'Sun', delivered: 156, onTime: 148, delayed: 8 }
        ],
        regionDistribution: [
          { name: 'Zone A', value: 35, color: '#3B82F6' },
          { name: 'Zone B', value: 28, color: '#10B981' },
          { name: 'Zone C', value: 22, color: '#F59E0B' },
          { name: 'Zone D', value: 15, color: '#EF4444' }
        ],
        timeAnalysis: [
          { hour: '08:00', avgTime: 32, efficiency: 78 },
          { hour: '10:00', avgTime: 28, efficiency: 85 },
          { hour: '12:00', avgTime: 35, efficiency: 72 },
          { hour: '14:00', avgTime: 25, efficiency: 92 },
          { hour: '16:00', avgTime: 30, efficiency: 80 },
          { hour: '18:00', avgTime: 38, efficiency: 68 }
        ]
      });
    } catch (error) {
      console.error('Failed to fetch analytics:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const exportReport = () => {
    // In a real app, this would generate and download a comprehensive report
    console.log('Exporting analytics report...');
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <LoadingSpinner size="lg" text="Loading analytics..." />
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="bg-gradient-to-r from-indigo-600 to-indigo-800 rounded-xl p-8 text-white">
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold mb-2">Performance Analytics</h1>
            <p className="text-indigo-100">Comprehensive insights into delivery operations and optimization results</p>
          </div>
          <div className="flex items-center space-x-4">
            <select
              value={timeRange}
              onChange={(e) => setTimeRange(e.target.value)}
              className="px-4 py-2 bg-white text-gray-800 rounded-lg border-0 focus:outline-none focus:ring-2 focus:ring-indigo-500"
            >
              <option value="7d">Last 7 Days</option>
              <option value="30d">Last 30 Days</option>
              <option value="90d">Last 90 Days</option>
              <option value="1y">Last Year</option>
            </select>
            <button
              onClick={exportReport}
              className="flex items-center space-x-2 px-4 py-2 bg-white text-indigo-600 rounded-lg hover:bg-gray-50 transition-colors"
            >
              <Download className="h-5 w-5" />
              <span>Export Report</span>
            </button>
          </div>
        </div>
      </div>

      {/* Summary Metrics */}
      {analyticsData && (
        <>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <MetricCard
              title="Total Cost Savings"
              value={`$${(analyticsData.summary.totalCostSavings / 1000).toFixed(0)}K`}
              change="+15.3% vs last period"
              changeType="positive"
              icon={DollarSign}
              color="green"
            />
            <MetricCard
              title="Avg Delivery Time"
              value={`${analyticsData.summary.avgDeliveryTime} min`}
              change="-8.2% improvement"
              changeType="positive"
              icon={Clock}
              color="blue"
            />
            <MetricCard
              title="Route Efficiency"
              value={`${analyticsData.summary.routeEfficiency}%`}
              change="+4.1% optimized"
              changeType="positive"
              icon={TrendingUp}
              color="orange"
            />
            <MetricCard
              title="Fuel Savings"
              value={`${analyticsData.summary.fuelSavings}%`}
              change="+2.8% efficiency"
              changeType="positive"
              icon={Package}
              color="green"
            />
          </div>

          {/* Charts Grid */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            {/* Cost Analysis */}
            <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
              <h3 className="text-lg font-semibold text-gray-800 mb-4">Cost Analysis - Before vs After Optimization</h3>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={analyticsData.costAnalysis}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="month" />
                  <YAxis />
                  <Tooltip formatter={(value) => [`$${value.toLocaleString()}`, '']} />
                  <Legend />
                  <Bar dataKey="beforeOptimization" fill="#EF4444" name="Before Optimization" />
                  <Bar dataKey="afterOptimization" fill="#10B981" name="After Optimization" />
                </BarChart>
              </ResponsiveContainer>
            </div>

            {/* Delivery Performance */}
            <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
              <h3 className="text-lg font-semibold text-gray-800 mb-4">Weekly Delivery Performance</h3>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={analyticsData.deliveryPerformance}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="day" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Bar dataKey="onTime" stackId="a" fill="#10B981" name="On Time" />
                  <Bar dataKey="delayed" stackId="a" fill="#EF4444" name="Delayed" />
                </BarChart>
              </ResponsiveContainer>
            </div>

            {/* Region Distribution */}
            <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
              <h3 className="text-lg font-semibold text-gray-800 mb-4">Delivery Distribution by Region</h3>
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={analyticsData.regionDistribution}
                    cx="50%"
                    cy="50%"
                    outerRadius={100}
                    fill="#8884d8"
                    dataKey="value"
                    label={({ name, value }) => `${name}: ${value}%`}
                  >
                    {analyticsData.regionDistribution.map((entry: any, index: number) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip formatter={(value) => [`${value}%`, 'Distribution']} />
                </PieChart>
              </ResponsiveContainer>
            </div>

            {/* Time Analysis */}
            <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
              <h3 className="text-lg font-semibold text-gray-800 mb-4">Time-based Performance Analysis</h3>
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={analyticsData.timeAnalysis}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="hour" />
                  <YAxis yAxisId="left" />
                  <YAxis yAxisId="right" orientation="right" />
                  <Tooltip />
                  <Legend />
                  <Bar yAxisId="left" dataKey="avgTime" fill="#3B82F6" name="Avg Time (min)" />
                  <Line 
                    yAxisId="right" 
                    type="monotone" 
                    dataKey="efficiency" 
                    stroke="#10B981" 
                    strokeWidth={3}
                    name="Efficiency (%)"
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Detailed Statistics */}
          <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
            <h3 className="text-lg font-semibold text-gray-800 mb-6">Detailed Performance Statistics</h3>
            
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              <div className="text-center p-4 bg-blue-50 rounded-lg">
                <h4 className="text-2xl font-bold text-blue-600">2,847</h4>
                <p className="text-sm text-blue-700">Total Deliveries</p>
                <p className="text-xs text-blue-600 mt-1">+12.3% vs last month</p>
              </div>
              
              <div className="text-center p-4 bg-green-50 rounded-lg">
                <h4 className="text-2xl font-bold text-green-600">97.2%</h4>
                <p className="text-sm text-green-700">On-time Delivery Rate</p>
                <p className="text-xs text-green-600 mt-1">+2.1% improvement</p>
              </div>
              
              <div className="text-center p-4 bg-orange-50 rounded-lg">
                <h4 className="text-2xl font-bold text-orange-600">1,234 km</h4>
                <p className="text-sm text-orange-700">Distance Saved</p>
                <p className="text-xs text-orange-600 mt-1">18.5% optimization</p>
              </div>
              
              <div className="text-center p-4 bg-purple-50 rounded-lg">
                <h4 className="text-2xl font-bold text-purple-600">156 hrs</h4>
                <p className="text-sm text-purple-700">Time Saved</p>
                <p className="text-xs text-purple-600 mt-1">23.7% efficiency gain</p>
              </div>
            </div>
            
            <div className="mt-8 grid grid-cols-1 lg:grid-cols-2 gap-6">
              <div className="p-4 border border-gray-200 rounded-lg">
                <h4 className="font-medium text-gray-800 mb-3">Top Performing Routes</h4>
                <div className="space-y-2">
                  <div className="flex justify-between items-center text-sm">
                    <span className="text-gray-600">Route A (Central District)</span>
                    <span className="font-medium text-green-600">98.5% efficiency</span>
                  </div>
                  <div className="flex justify-between items-center text-sm">
                    <span className="text-gray-600">Route B (North Zone)</span>
                    <span className="font-medium text-green-600">96.2% efficiency</span>
                  </div>
                  <div className="flex justify-between items-center text-sm">
                    <span className="text-gray-600">Route C (East Corridor)</span>
                    <span className="font-medium text-green-600">94.8% efficiency</span>
                  </div>
                </div>
              </div>
              
              <div className="p-4 border border-gray-200 rounded-lg">
                <h4 className="font-medium text-gray-800 mb-3">Optimization Impact</h4>
                <div className="space-y-2">
                  <div className="flex justify-between items-center text-sm">
                    <span className="text-gray-600">CO2 Emissions Reduced</span>
                    <span className="font-medium text-green-600">-847 kg</span>
                  </div>
                  <div className="flex justify-between items-center text-sm">
                    <span className="text-gray-600">Fuel Cost Savings</span>
                    <span className="font-medium text-green-600">$3,420</span>
                  </div>
                  <div className="flex justify-between items-center text-sm">
                    <span className="text-gray-600">Driver Overtime Reduced</span>
                    <span className="font-medium text-green-600">-23.5%</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </>
      )}
    </div>
  );
};

export default Analytics;