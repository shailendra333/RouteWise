import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  Package, 
  DollarSign, 
  Clock, 
  TrendingUp,
  MapPin,
  Truck,
  Users,
  AlertTriangle
} from 'lucide-react';
import MetricCard from '../components/MetricCard';
import LoadingSpinner from '../components/LoadingSpinner';
import { useAuth } from '../contexts/AuthContext';
import { Line } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
);

const Dashboard: React.FC = () => {
  const { isAuthenticated } = useAuth();
  const navigate = useNavigate();
  const [isLoading, setIsLoading] = useState(true);
  const [metrics, setMetrics] = useState({
    totalDeliveries: 0,
    costSavings: 0,
    avgDeliveryTime: 0,
    efficiency: 0,
    activeRoutes: 0,
    totalDrivers: 0,
    pendingOrders: 0,
    fuelSavings: 0
  });

  useEffect(() => {
    if (!isAuthenticated) {
      navigate('/login');
      return;
    }

    // Simulate API call to fetch dashboard metrics
    const fetchMetrics = async () => {
      setIsLoading(true);
      try {
        // Simulate API delay
        await new Promise(resolve => setTimeout(resolve, 1000));
        
        setMetrics({
          totalDeliveries: 1247,
          costSavings: 23.5,
          avgDeliveryTime: 28,
          efficiency: 94.2,
          activeRoutes: 12,
          totalDrivers: 18,
          pendingOrders: 156,
          fuelSavings: 18.7
        });
      } catch (error) {
        console.error('Error fetching metrics:', error);
      } finally {
        setIsLoading(false);
      }
    };

    fetchMetrics();
  }, [isAuthenticated, navigate]);

  const demandData = {
    labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
    datasets: [
      {
        label: 'Predicted Demand',
        data: [1200, 1350, 1100, 1400, 1600, 1550],
        borderColor: 'rgb(37, 99, 235)',
        backgroundColor: 'rgba(37, 99, 235, 0.1)',
        tension: 0.4,
      },
      {
        label: 'Actual Demand',
        data: [1180, 1320, 1150, 1380, 1580, null],
        borderColor: 'rgb(5, 150, 105)',
        backgroundColor: 'rgba(5, 150, 105, 0.1)',
        tension: 0.4,
      },
    ],
  };

  const chartOptions = {
    responsive: true,
    plugins: {
      legend: {
        position: 'top' as const,
      },
      title: {
        display: true,
        text: 'Demand Forecasting Accuracy',
      },
    },
    scales: {
      y: {
        beginAtZero: true,
      },
    },
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <LoadingSpinner size="lg" text="Loading dashboard..." />
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="bg-gradient-to-r from-blue-600 to-blue-800 rounded-xl p-8 text-white">
        <h1 className="text-3xl font-bold mb-2">Smart Logistics Dashboard</h1>
        <p className="text-blue-100">Monitor your delivery operations and AI-powered optimizations in real-time</p>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <MetricCard
          title="Total Deliveries"
          value={metrics.totalDeliveries.toLocaleString()}
          change="+12.5% from last month"
          changeType="positive"
          icon={Package}
          color="blue"
        />
        <MetricCard
          title="Cost Savings"
          value={`${metrics.costSavings}%`}
          change="+3.2% improvement"
          changeType="positive"
          icon={DollarSign}
          color="green"
        />
        <MetricCard
          title="Avg Delivery Time"
          value={`${metrics.avgDeliveryTime} min`}
          change="-5.1% faster"
          changeType="positive"
          icon={Clock}
          color="orange"
        />
        <MetricCard
          title="Route Efficiency"
          value={`${metrics.efficiency}%`}
          change="+2.8% optimized"
          changeType="positive"
          icon={TrendingUp}
          color="blue"
        />
      </div>

      {/* Secondary Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <MetricCard
          title="Active Routes"
          value={metrics.activeRoutes}
          icon={MapPin}
          color="blue"
        />
        <MetricCard
          title="Total Drivers"
          value={metrics.totalDrivers}
          icon={Users}
          color="green"
        />
        <MetricCard
          title="Pending Orders"
          value={metrics.pendingOrders}
          icon={AlertTriangle}
          color="orange"
        />
        <MetricCard
          title="Fuel Savings"
          value={`${metrics.fuelSavings}%`}
          change="+4.2% efficiency"
          changeType="positive"
          icon={Truck}
          color="green"
        />
      </div>

      {/* Charts and Analytics */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Demand Forecasting Chart */}
        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
          <h3 className="text-lg font-semibold text-gray-800 mb-4">Demand Forecasting</h3>
          <Line data={demandData} options={chartOptions} />
        </div>

        {/* Recent Activities */}
        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
          <h3 className="text-lg font-semibold text-gray-800 mb-4">Recent Activities</h3>
          <div className="space-y-4">
            <div className="flex items-center space-x-3 p-3 bg-green-50 rounded-lg">
              <div className="p-2 bg-green-100 rounded-full">
                <Package className="h-4 w-4 text-green-600" />
              </div>
              <div>
                <p className="text-sm font-medium text-gray-800">Route optimization completed</p>
                <p className="text-xs text-gray-600">Saved 23 minutes on Zone A deliveries</p>
              </div>
            </div>
            <div className="flex items-center space-x-3 p-3 bg-blue-50 rounded-lg">
              <div className="p-2 bg-blue-100 rounded-full">
                <TrendingUp className="h-4 w-4 text-blue-600" />
              </div>
              <div>
                <p className="text-sm font-medium text-gray-800">Demand forecast updated</p>
                <p className="text-xs text-gray-600">95.8% accuracy for next week predictions</p>
              </div>
            </div>
            <div className="flex items-center space-x-3 p-3 bg-orange-50 rounded-lg">
              <div className="p-2 bg-orange-100 rounded-full">
                <Truck className="h-4 w-4 text-orange-600" />
              </div>
              <div>
                <p className="text-sm font-medium text-gray-800">New delivery zone added</p>
                <p className="text-xs text-gray-600">Zone D coverage expanded by 15%</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
        <h3 className="text-lg font-semibold text-gray-800 mb-4">Quick Actions</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <button
            onClick={() => navigate('/route-optimization')}
            className="p-4 text-left border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
          >
            <MapPin className="h-6 w-6 text-blue-600 mb-2" />
            <h4 className="font-medium text-gray-800">Optimize Routes</h4>
            <p className="text-sm text-gray-600">Create optimized delivery routes</p>
          </button>
          <button
            onClick={() => navigate('/demand-forecasting')}
            className="p-4 text-left border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
          >
            <TrendingUp className="h-6 w-6 text-green-600 mb-2" />
            <h4 className="font-medium text-gray-800">Forecast Demand</h4>
            <p className="text-sm text-gray-600">Predict future delivery demand</p>
          </button>
          <button
            onClick={() => navigate('/data-management')}
            className="p-4 text-left border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
          >
            <Package className="h-6 w-6 text-orange-600 mb-2" />
            <h4 className="font-medium text-gray-800">Manage Data</h4>
            <p className="text-sm text-gray-600">Upload and manage datasets</p>
          </button>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;