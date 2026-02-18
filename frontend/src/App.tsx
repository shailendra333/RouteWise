import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Navbar from './components/Navbar';
import Dashboard from './pages/Dashboard';
import DemandForecasting from './pages/DemandForecasting';
import RouteOptimization from './pages/RouteOptimization';
import DataManagement from './pages/DataManagement';
import Analytics from './pages/Analytics';
import Login from './pages/Login';
import AIAgents from './pages/AIAgents';
import AgentComparison from './pages/AgentComparison';
import { AuthProvider } from './contexts/AuthContext';

function App() {
  return (
    <AuthProvider>
      <Router>
        <div className="min-h-screen bg-gray-50">
          <Navbar />
          <main className="container mx-auto px-4 py-8">
            <Routes>
              <Route path="/login" element={<Login />} />
              <Route path="/" element={<Dashboard />} />
              <Route path="/demand-forecasting" element={<DemandForecasting />} />
              <Route path="/route-optimization" element={<RouteOptimization />} />
              <Route path="/data-management" element={<DataManagement />} />
              <Route path="/analytics" element={<Analytics />} />
              <Route path="/ai-agents" element={<AIAgents />} />
              <Route path="/agent-comparison" element={<AgentComparison />} />
            </Routes>
          </main>
        </div>
      </Router>
    </AuthProvider>
  );
}

export default App;