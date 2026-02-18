import React, { useState, useEffect } from 'react';
import { MapContainer, TileLayer, Marker, Popup, Polyline } from 'react-leaflet';
import { LatLngTuple } from 'leaflet';
import { Navigation, Plus, Trash2, Play, Download, Settings } from 'lucide-react';
import LoadingSpinner from '../components/LoadingSpinner';
import 'leaflet/dist/leaflet.css';

// Fix for default markers in react-leaflet
import L from 'leaflet';
import markerIcon from 'leaflet/dist/images/marker-icon.png';
import markerShadow from 'leaflet/dist/images/marker-shadow.png';
import markerRetina from 'leaflet/dist/images/marker-icon-2x.png';

delete (L.Icon.Default.prototype as any)._getIconUrl;
L.Icon.Default.mergeOptions({
  iconUrl: markerIcon,
  iconRetinaUrl: markerRetina,
  shadowUrl: markerShadow,
});

interface DeliveryPoint {
  id: number;
  address: string;
  coordinates: LatLngTuple;
  priority: 'High' | 'Medium' | 'Low';
  timeWindow?: string;
}

const RouteOptimization: React.FC = () => {
  const [deliveryPoints, setDeliveryPoints] = useState<DeliveryPoint[]>([
    { id: 1, address: "Central Park, NYC", coordinates: [40.7829, -73.9654], priority: 'High', timeWindow: '09:00-11:00' },
    { id: 2, address: "Times Square, NYC", coordinates: [40.7580, -73.9855], priority: 'Medium', timeWindow: '11:00-13:00' },
    { id: 3, address: "Brooklyn Bridge, NYC", coordinates: [40.7061, -73.9969], priority: 'High', timeWindow: '13:00-15:00' },
    { id: 4, address: "Empire State Building, NYC", coordinates: [40.7484, -73.9857], priority: 'Low', timeWindow: '15:00-17:00' },
    { id: 5, address: "Wall Street, NYC", coordinates: [40.7074, -74.0113], priority: 'Medium', timeWindow: '09:00-11:00' }
  ]);

  const [optimizedRoute, setOptimizedRoute] = useState<LatLngTuple[]>([]);
  const [isOptimizing, setIsOptimizing] = useState(false);
  const [routeMetrics, setRouteMetrics] = useState<any>(null);
  const [newPointAddress, setNewPointAddress] = useState('');
  const [vehicleCapacity, setVehicleCapacity] = useState(100);
  const [algorithmType, setAlgorithmType] = useState<'or-tools' | 'genetic'>('or-tools');

  const center: LatLngTuple = [40.7614, -73.9776]; // NYC

  const optimizeRoute = async () => {
    setIsOptimizing(true);
    try {
      // Simulate route optimization
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      // Create optimized route path
      const optimizedPath: LatLngTuple[] = [
        [40.7829, -73.9654], // Central Park
        [40.7580, -73.9855], // Times Square
        [40.7484, -73.9857], // Empire State
        [40.7061, -73.9969], // Brooklyn Bridge
        [40.7074, -74.0113], // Wall Street
        [40.7829, -73.9654], // Back to start
      ];
      
      setOptimizedRoute(optimizedPath);
      setRouteMetrics({
        totalDistance: 12.8,
        estimatedTime: 45,
        fuelSavings: 18.5,
        costSavings: 42.3,
        optimizationMethod: algorithmType === 'or-tools' ? 'OR-Tools TSP' : 'Genetic Algorithm'
      });
    } catch (error) {
      console.error('Optimization failed:', error);
    } finally {
      setIsOptimizing(false);
    }
  };

  const addDeliveryPoint = () => {
    if (newPointAddress.trim()) {
      // Simulate geocoding - in real app, you'd use a geocoding service
      const newPoint: DeliveryPoint = {
        id: Date.now(),
        address: newPointAddress,
        coordinates: [40.7614 + (Math.random() - 0.5) * 0.1, -73.9776 + (Math.random() - 0.5) * 0.1],
        priority: 'Medium'
      };
      setDeliveryPoints([...deliveryPoints, newPoint]);
      setNewPointAddress('');
    }
  };

  const removeDeliveryPoint = (id: number) => {
    setDeliveryPoints(deliveryPoints.filter(point => point.id !== id));
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'High': return '#ef4444';
      case 'Medium': return '#f59e0b';
      case 'Low': return '#10b981';
      default: return '#6b7280';
    }
  };

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="bg-gradient-to-r from-orange-600 to-orange-800 rounded-xl p-8 text-white">
        <h1 className="text-3xl font-bold mb-2">Route Optimization</h1>
        <p className="text-orange-100">Optimize delivery routes using advanced algorithms and real-time traffic data</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Controls Panel */}
        <div className="space-y-6">
          {/* Algorithm Settings */}
          <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
            <h3 className="text-lg font-semibold text-gray-800 mb-4 flex items-center space-x-2">
              <Settings className="h-5 w-5" />
              <span>Optimization Settings</span>
            </h3>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Algorithm</label>
                <select
                  value={algorithmType}
                  onChange={(e) => setAlgorithmType(e.target.value as 'or-tools' | 'genetic')}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500"
                >
                  <option value="or-tools">OR-Tools (TSP/VRP)</option>
                  <option value="genetic">Genetic Algorithm</option>
                </select>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Vehicle Capacity</label>
                <input
                  type="number"
                  value={vehicleCapacity}
                  onChange={(e) => setVehicleCapacity(Number(e.target.value))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500"
                />
              </div>

              <button
                onClick={optimizeRoute}
                disabled={isOptimizing || deliveryPoints.length < 2}
                className="w-full flex items-center justify-center space-x-2 py-3 px-4 bg-orange-600 hover:bg-orange-700 disabled:bg-gray-400 text-white rounded-lg transition-colors"
              >
                {isOptimizing ? (
                  <LoadingSpinner size="sm" />
                ) : (
                  <>
                    <Play className="h-5 w-5" />
                    <span>Optimize Route</span>
                  </>
                )}
              </button>
            </div>
          </div>

          {/* Add Delivery Point */}
          <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
            <h3 className="text-lg font-semibold text-gray-800 mb-4 flex items-center space-x-2">
              <Plus className="h-5 w-5" />
              <span>Add Delivery Point</span>
            </h3>
            
            <div className="space-y-3">
              <input
                type="text"
                placeholder="Enter address..."
                value={newPointAddress}
                onChange={(e) => setNewPointAddress(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500"
                onKeyPress={(e) => e.key === 'Enter' && addDeliveryPoint()}
              />
              <button
                onClick={addDeliveryPoint}
                disabled={!newPointAddress.trim()}
                className="w-full flex items-center justify-center space-x-2 py-2 px-4 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white rounded-lg transition-colors"
              >
                <Plus className="h-4 w-4" />
                <span>Add Point</span>
              </button>
            </div>
          </div>

          {/* Delivery Points List */}
          <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
            <h3 className="text-lg font-semibold text-gray-800 mb-4">Delivery Points ({deliveryPoints.length})</h3>
            <div className="space-y-2 max-h-64 overflow-y-auto">
              {deliveryPoints.map((point) => (
                <div key={point.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                  <div className="flex-1">
                    <p className="text-sm font-medium text-gray-800">{point.address}</p>
                    <div className="flex items-center space-x-2 mt-1">
                      <span 
                        className="px-2 py-1 text-xs rounded-full text-white"
                        style={{ backgroundColor: getPriorityColor(point.priority) }}
                      >
                        {point.priority}
                      </span>
                      {point.timeWindow && (
                        <span className="text-xs text-gray-600">{point.timeWindow}</span>
                      )}
                    </div>
                  </div>
                  <button
                    onClick={() => removeDeliveryPoint(point.id)}
                    className="p-1 text-red-600 hover:text-red-800 transition-colors"
                  >
                    <Trash2 className="h-4 w-4" />
                  </button>
                </div>
              ))}
            </div>
          </div>

          {/* Route Metrics */}
          {routeMetrics && (
            <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
              <div className="flex justify-between items-center mb-4">
                <h3 className="text-lg font-semibold text-gray-800">Route Metrics</h3>
                <button className="flex items-center space-x-2 px-3 py-1 text-sm bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors">
                  <Download className="h-4 w-4" />
                  <span>Export</span>
                </button>
              </div>
              
              <div className="space-y-3">
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">Total Distance</span>
                  <span className="text-sm font-medium">{routeMetrics.totalDistance} km</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">Estimated Time</span>
                  <span className="text-sm font-medium">{routeMetrics.estimatedTime} min</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">Fuel Savings</span>
                  <span className="text-sm font-medium text-green-600">+{routeMetrics.fuelSavings}%</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">Cost Savings</span>
                  <span className="text-sm font-medium text-green-600">+{routeMetrics.costSavings}%</span>
                </div>
                <div className="pt-2 border-t border-gray-200">
                  <span className="text-xs text-gray-500">Method: {routeMetrics.optimizationMethod}</span>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Map */}
        <div className="lg:col-span-2">
          <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-lg font-semibold text-gray-800 flex items-center space-x-2">
                <Navigation className="h-5 w-5" />
                <span>Route Visualization</span>
              </h3>
              <div className="flex items-center space-x-2 text-sm text-gray-600">
                <div className="flex items-center space-x-1">
                  <div className="w-3 h-3 bg-red-500 rounded-full"></div>
                  <span>High Priority</span>
                </div>
                <div className="flex items-center space-x-1">
                  <div className="w-3 h-3 bg-yellow-500 rounded-full"></div>
                  <span>Medium Priority</span>
                </div>
                <div className="flex items-center space-x-1">
                  <div className="w-3 h-3 bg-green-500 rounded-full"></div>
                  <span>Low Priority</span>
                </div>
              </div>
            </div>
            
            <div className="h-96 rounded-lg overflow-hidden border border-gray-200">
              <MapContainer
                center={center}
                zoom={12}
                style={{ height: '100%', width: '100%' }}
              >
                <TileLayer
                  attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
                  url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                />
                
                {/* Delivery Points */}
                {deliveryPoints.map((point) => (
                  <Marker key={point.id} position={point.coordinates}>
                    <Popup>
                      <div className="p-2">
                        <h4 className="font-medium">{point.address}</h4>
                        <p className="text-sm text-gray-600">Priority: {point.priority}</p>
                        {point.timeWindow && (
                          <p className="text-sm text-gray-600">Time: {point.timeWindow}</p>
                        )}
                      </div>
                    </Popup>
                  </Marker>
                ))}
                
                {/* Optimized Route */}
                {optimizedRoute.length > 0 && (
                  <Polyline
                    positions={optimizedRoute}
                    color="#ea580c"
                    weight={4}
                    opacity={0.8}
                  />
                )}
              </MapContainer>
            </div>
            
            {optimizedRoute.length > 0 && (
              <div className="mt-4 p-4 bg-green-50 border border-green-200 rounded-lg">
                <p className="text-sm text-green-700">
                  ✓ Route optimized successfully! The orange line shows the most efficient delivery path.
                </p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default RouteOptimization;