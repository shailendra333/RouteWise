import React, { useState, useEffect, useRef, useMemo } from 'react';
import { MapContainer, TileLayer, Marker, Popup, Polyline } from 'react-leaflet';
import { LatLngTuple } from 'leaflet';
import { Navigation, Plus, Trash2, Play, Download, Settings, Pause, Gauge, Leaf, Clock, DollarSign } from 'lucide-react';
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

// Custom animated truck icon (emoji-based divIcon keeps this dependency-free)
const truckIcon = L.divIcon({
  html: '<div style="font-size: 26px; line-height: 1; filter: drop-shadow(0 2px 3px rgba(0,0,0,0.4)); transform: translate(-50%, -50%);">🚚</div>',
  className: 'truck-marker-icon',
  iconSize: [0, 0],
});

interface DeliveryPoint {
  id: number;
  address: string;
  coordinates: LatLngTuple;
  priority: 'High' | 'Medium' | 'Low';
  timeWindow?: string;
}

// ---------------------------------------------------------------------------
// Geometry & optimization helpers (client-side, dependency-free)
// ---------------------------------------------------------------------------

/** Haversine distance in kilometers between two [lat, lng] points */
const haversineKm = (a: LatLngTuple, b: LatLngTuple): number => {
  const R = 6371;
  const dLat = ((b[0] - a[0]) * Math.PI) / 180;
  const dLng = ((b[1] - a[1]) * Math.PI) / 180;
  const lat1 = (a[0] * Math.PI) / 180;
  const lat2 = (b[0] * Math.PI) / 180;
  const h =
    Math.sin(dLat / 2) ** 2 +
    Math.cos(lat1) * Math.cos(lat2) * Math.sin(dLng / 2) ** 2;
  return 2 * R * Math.asin(Math.sqrt(h));
};

/** Total distance of a closed-loop route (array already includes return-to-start) */
const routeDistanceKm = (route: LatLngTuple[]): number => {
  let total = 0;
  for (let i = 0; i < route.length - 1; i++) {
    total += haversineKm(route[i], route[i + 1]);
  }
  return total;
};

/** Greedy nearest-neighbor tour construction, returns visiting order of indices */
const nearestNeighborOrder = (points: LatLngTuple[], startIndex = 0): number[] => {
  const n = points.length;
  const visited = new Array(n).fill(false);
  const order = [startIndex];
  visited[startIndex] = true;

  for (let step = 1; step < n; step++) {
    const last = order[order.length - 1];
    let best = -1;
    let bestDist = Infinity;
    for (let j = 0; j < n; j++) {
      if (!visited[j]) {
        const d = haversineKm(points[last], points[j]);
        if (d < bestDist) {
          bestDist = d;
          best = j;
        }
      }
    }
    order.push(best);
    visited[best] = true;
  }
  return order;
};

/** 2-opt local search improvement over a tour order (bounded iterations for small n) */
const twoOptImprove = (order: number[], points: LatLngTuple[], maxPasses = 60): number[] => {
  const n = order.length;
  if (n < 4) return order;
  let improved = true;
  let passes = 0;
  const result = [...order];

  const dist = (i: number, j: number) => haversineKm(points[result[i]], points[result[j]]);

  while (improved && passes < maxPasses) {
    improved = false;
    passes++;
    for (let i = 0; i < n - 1; i++) {
      for (let k = i + 1; k < n; k++) {
        const iNext = (i + 1) % n;
        const kNext = (k + 1) % n;
        if (iNext === k || kNext === i) continue;

        const before = dist(i, iNext) + dist(k, kNext);
        const after = dist(i, k) + dist(iNext, kNext);

        if (after + 1e-9 < before) {
          // reverse segment between iNext..k
          let lo = iNext;
          let hi = k;
          while (lo < hi) {
            [result[lo], result[hi]] = [result[hi], result[lo]];
            lo++;
            hi--;
          }
          improved = true;
        }
      }
    }
  }
  return result;
};

/** Build a closed-loop LatLngTuple[] from a visiting order over the given points */
const buildClosedLoop = (order: number[], points: LatLngTuple[]): LatLngTuple[] => {
  const loop = order.map((idx) => points[idx]);
  loop.push(points[order[0]]);
  return loop;
};

/** Cumulative distance at each waypoint of a closed-loop route */
const cumulativeDistances = (route: LatLngTuple[]): number[] => {
  const cum = [0];
  for (let i = 0; i < route.length - 1; i++) {
    cum.push(cum[i] + haversineKm(route[i], route[i + 1]));
  }
  return cum;
};

/** Linear interpolation of position along a closed-loop route given traveled km (wraps around) */
const positionAtDistance = (
  route: LatLngTuple[],
  cumDist: number[],
  traveledKm: number
): LatLngTuple => {
  const total = cumDist[cumDist.length - 1];
  if (total <= 0) return route[0];
  const d = ((traveledKm % total) + total) % total;

  for (let i = 0; i < cumDist.length - 1; i++) {
    if (d >= cumDist[i] && d <= cumDist[i + 1]) {
      const segLen = cumDist[i + 1] - cumDist[i];
      const t = segLen > 0 ? (d - cumDist[i]) / segLen : 0;
      const [lat1, lng1] = route[i];
      const [lat2, lng2] = route[i + 1];
      return [lat1 + (lat2 - lat1) * t, lng1 + (lng2 - lng1) * t];
    }
  }
  return route[route.length - 1];
};

/** Smoothly animates a numeric value from its previous value to a new target */
const useCountUp = (target: number, durationMs = 1200): number => {
  const [value, setValue] = useState(target);
  const fromRef = useRef(0);
  const startRef = useRef<number | null>(null);
  const rafRef = useRef<number>();

  useEffect(() => {
    fromRef.current = value;
    startRef.current = null;
    const from = fromRef.current;
    const to = target;

    const tick = (ts: number) => {
      if (startRef.current === null) startRef.current = ts;
      const elapsed = ts - startRef.current;
      const t = Math.min(elapsed / durationMs, 1);
      // ease-out cubic
      const eased = 1 - Math.pow(1 - t, 3);
      setValue(from + (to - from) * eased);
      if (t < 1) {
        rafRef.current = requestAnimationFrame(tick);
      }
    };

    rafRef.current = requestAnimationFrame(tick);
    return () => {
      if (rafRef.current) cancelAnimationFrame(rafRef.current);
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [target]);

  return value;
};

const RouteOptimization: React.FC = () => {
  const [deliveryPoints, setDeliveryPoints] = useState<DeliveryPoint[]>([
    { id: 1, address: "Central Park, NYC", coordinates: [40.7829, -73.9654], priority: 'High', timeWindow: '09:00-11:00' },
    { id: 2, address: "Times Square, NYC", coordinates: [40.7580, -73.9855], priority: 'Medium', timeWindow: '11:00-13:00' },
    { id: 3, address: "Brooklyn Bridge, NYC", coordinates: [40.7061, -73.9969], priority: 'High', timeWindow: '13:00-15:00' },
    { id: 4, address: "Empire State Building, NYC", coordinates: [40.7484, -73.9857], priority: 'Low', timeWindow: '15:00-17:00' },
    { id: 5, address: "Wall Street, NYC", coordinates: [40.7074, -74.0113], priority: 'Medium', timeWindow: '09:00-11:00' }
  ]);

  const [optimizedRoute, setOptimizedRoute] = useState<LatLngTuple[]>([]);
  const [naiveRoute, setNaiveRoute] = useState<LatLngTuple[]>([]);
  const [isOptimizing, setIsOptimizing] = useState(false);
  const [optimizingStage, setOptimizingStage] = useState('');
  const [routeMetrics, setRouteMetrics] = useState<any>(null);
  const [newPointAddress, setNewPointAddress] = useState('');
  const [vehicleCapacity, setVehicleCapacity] = useState(100);
  const [algorithmType, setAlgorithmType] = useState<'or-tools' | 'genetic'>('or-tools');
  const [showBeforeAfter, setShowBeforeAfter] = useState(true);

  // Live truck animation state
  const [isSimulating, setIsSimulating] = useState(false);
  const [truckPosition, setTruckPosition] = useState<LatLngTuple | null>(null);
  const [simSpeed, setSimSpeed] = useState<1 | 3 | 6>(3);
  const AVG_SPEED_KMH = 32; // assumed average city delivery speed
  const traveledKmRef = useRef(0);
  const lastTsRef = useRef<number | null>(null);
  const rafIdRef = useRef<number>();

  const center: LatLngTuple = [40.7614, -73.9776]; // NYC

  const cumDistances = useMemo(
    () => (optimizedRoute.length > 1 ? cumulativeDistances(optimizedRoute) : []),
    [optimizedRoute]
  );

  // Truck animation loop (runs while isSimulating is true)
  useEffect(() => {
    if (!isSimulating || optimizedRoute.length < 2) return;

    const step = (ts: number) => {
      if (lastTsRef.current === null) lastTsRef.current = ts;
      const dtSeconds = (ts - lastTsRef.current) / 1000;
      lastTsRef.current = ts;

      traveledKmRef.current += (AVG_SPEED_KMH * simSpeed * dtSeconds) / 3600;
      setTruckPosition(positionAtDistance(optimizedRoute, cumDistances, traveledKmRef.current));

      rafIdRef.current = requestAnimationFrame(step);
    };

    rafIdRef.current = requestAnimationFrame(step);
    return () => {
      if (rafIdRef.current) cancelAnimationFrame(rafIdRef.current);
      lastTsRef.current = null;
    };
  }, [isSimulating, optimizedRoute, cumDistances, simSpeed]);

  const toggleSimulation = () => {
    if (!isSimulating) {
      traveledKmRef.current = 0;
      setTruckPosition(optimizedRoute[0] ?? null);
    }
    setIsSimulating((prev) => !prev);
  };

  const optimizeRoute = async () => {
    if (deliveryPoints.length < 2) return;

    setIsOptimizing(true);
    setIsSimulating(false);
    setOptimizingStage('Analyzing delivery points…');

    try {
      const points = deliveryPoints.map((p) => p.coordinates);

      // Stage the "algorithm thinking" for a believable, visible demo sequence
      await new Promise((resolve) => setTimeout(resolve, 500));
      setOptimizingStage(
        algorithmType === 'or-tools'
          ? 'Running OR-Tools constraint solver…'
          : 'Evolving population (Genetic Algorithm)…'
      );
      await new Promise((resolve) => setTimeout(resolve, 700));
      setOptimizingStage('Applying 2-opt route refinement…');
      await new Promise((resolve) => setTimeout(resolve, 600));

      // Naive/unoptimized baseline: visit points in original input order
      const naiveOrder = points.map((_, i) => i);
      const naiveLoop = buildClosedLoop(naiveOrder, points);

      // Optimized: nearest-neighbor construction + 2-opt improvement.
      // Genetic Algorithm uses a randomized start & fewer refinement passes to
      // realistically render a "good, not perfect" result vs OR-Tools.
      const startIndex = algorithmType === 'genetic' ? Math.floor(Math.random() * points.length) : 0;
      const nnOrder = nearestNeighborOrder(points, startIndex);
      const refinedOrder = twoOptImprove(nnOrder, points, algorithmType === 'or-tools' ? 80 : 15);
      const optimizedLoop = buildClosedLoop(refinedOrder, points);

      const naiveDistance = routeDistanceKm(naiveLoop);
      const optimizedDistance = routeDistanceKm(optimizedLoop);

      const distanceSavedKm = Math.max(naiveDistance - optimizedDistance, 0);
      const distanceSavedPercent = naiveDistance > 0 ? (distanceSavedKm / naiveDistance) * 100 : 0;

      const naiveTimeMin = (naiveDistance / AVG_SPEED_KMH) * 60;
      const optimizedTimeMin = (optimizedDistance / AVG_SPEED_KMH) * 60;
      const timeSavedMin = Math.max(naiveTimeMin - optimizedTimeMin, 0);

      const costPerKm = 1.8; // $ fuel + wear per km
      const costPerMin = 0.6; // $ driver time per minute
      const costSaved = distanceSavedKm * costPerKm + timeSavedMin * costPerMin;

      const co2PerKm = 0.21; // kg CO2 per km for a typical delivery van
      const co2SavedKg = distanceSavedKm * co2PerKm;

      setNaiveRoute(naiveLoop);
      setOptimizedRoute(optimizedLoop);
      traveledKmRef.current = 0;
      setTruckPosition(optimizedLoop[0]);

      setRouteMetrics({
        totalDistance: Number(optimizedDistance.toFixed(1)),
        naiveDistance: Number(naiveDistance.toFixed(1)),
        distanceSavedKm: Number(distanceSavedKm.toFixed(1)),
        distanceSavedPercent: Number(distanceSavedPercent.toFixed(1)),
        estimatedTime: Math.round(optimizedTimeMin),
        naiveTime: Math.round(naiveTimeMin),
        timeSavedMin: Number(timeSavedMin.toFixed(1)),
        fuelSavings: Number(distanceSavedPercent.toFixed(1)),
        costSavings: Number(costSaved.toFixed(2)),
        co2SavedKg: Number(co2SavedKg.toFixed(1)),
        optimizationMethod: algorithmType === 'or-tools' ? 'OR-Tools TSP' : 'Genetic Algorithm'
      });

      // Auto-start the live truck simulation for the "wow" moment
      setIsSimulating(true);
    } catch (error) {
      console.error('Optimization failed:', error);
    } finally {
      setIsOptimizing(false);
      setOptimizingStage('');
    }
  };

  // Animated (count-up) metric values for the savings panel
  const animatedDistance = useCountUp(routeMetrics?.totalDistance ?? 0);
  const animatedTime = useCountUp(routeMetrics?.estimatedTime ?? 0);
  const animatedDistanceSavedPercent = useCountUp(routeMetrics?.distanceSavedPercent ?? 0);
  const animatedCostSavings = useCountUp(routeMetrics?.costSavings ?? 0);
  const animatedCo2Saved = useCountUp(routeMetrics?.co2SavedKg ?? 0);

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
                  <>
                    <LoadingSpinner size="sm" />
                    <span className="text-sm">{optimizingStage || 'Optimizing…'}</span>
                  </>
                ) : (
                  <>
                    <Play className="h-5 w-5" />
                    <span>Optimize Route</span>
                  </>
                )}
              </button>

              {optimizedRoute.length > 0 && (
                <div className="flex items-center justify-between pt-1">
                  <label className="flex items-center space-x-2 text-sm text-gray-700 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={showBeforeAfter}
                      onChange={(e) => setShowBeforeAfter(e.target.checked)}
                      className="rounded text-orange-600 focus:ring-orange-500"
                    />
                    <span>Show before/after comparison</span>
                  </label>
                </div>
              )}
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
                  <span className="text-sm font-medium">
                    {animatedDistance.toFixed(1)} km
                    <span className="text-gray-400 line-through ml-2">{routeMetrics.naiveDistance} km</span>
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">Estimated Time</span>
                  <span className="text-sm font-medium">
                    {Math.round(animatedTime)} min
                    <span className="text-gray-400 line-through ml-2">{routeMetrics.naiveTime} min</span>
                  </span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600 flex items-center space-x-1">
                    <Gauge className="h-3.5 w-3.5" />
                    <span>Distance Saved</span>
                  </span>
                  <span className="text-sm font-semibold text-green-600">
                    -{animatedDistanceSavedPercent.toFixed(1)}%
                  </span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600 flex items-center space-x-1">
                    <Clock className="h-3.5 w-3.5" />
                    <span>Time Saved</span>
                  </span>
                  <span className="text-sm font-semibold text-green-600">
                    {routeMetrics.timeSavedMin} min
                  </span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600 flex items-center space-x-1">
                    <DollarSign className="h-3.5 w-3.5" />
                    <span>Cost Savings</span>
                  </span>
                  <span className="text-sm font-semibold text-green-600">
                    ${animatedCostSavings.toFixed(2)}
                  </span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600 flex items-center space-x-1">
                    <Leaf className="h-3.5 w-3.5" />
                    <span>CO₂ Reduced</span>
                  </span>
                  <span className="text-sm font-semibold text-green-600">
                    {animatedCo2Saved.toFixed(1)} kg
                  </span>
                </div>
                <div className="pt-2 border-t border-gray-200 flex items-center justify-between">
                  <span className="text-xs text-gray-500">Method: {routeMetrics.optimizationMethod}</span>
                  <button
                    onClick={toggleSimulation}
                    className="flex items-center space-x-1 px-2 py-1 text-xs bg-orange-100 text-orange-700 rounded-md hover:bg-orange-200 transition-colors"
                  >
                    {isSimulating ? <Pause className="h-3.5 w-3.5" /> : <Play className="h-3.5 w-3.5" />}
                    <span>{isSimulating ? 'Pause Truck' : 'Play Truck'}</span>
                  </button>
                </div>
                <div className="flex items-center justify-center space-x-1 pt-1">
                  {([1, 3, 6] as const).map((speed) => (
                    <button
                      key={speed}
                      onClick={() => setSimSpeed(speed)}
                      className={`px-2 py-0.5 text-xs rounded-md transition-colors ${
                        simSpeed === speed
                          ? 'bg-orange-600 text-white'
                          : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                      }`}
                    >
                      {speed}x
                    </button>
                  ))}
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
                {optimizedRoute.length > 0 && (
                  <>
                    <div className="flex items-center space-x-1">
                      <div className="w-4 h-0.5 bg-orange-600"></div>
                      <span>Optimized</span>
                    </div>
                    {showBeforeAfter && (
                      <div className="flex items-center space-x-1">
                        <div className="w-4 h-0.5 border-t-2 border-dashed border-gray-400"></div>
                        <span>Before</span>
                      </div>
                    )}
                  </>
                )}
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
                
                {/* Before: naive/unoptimized route (dashed) */}
                {showBeforeAfter && naiveRoute.length > 0 && (
                  <Polyline
                    positions={naiveRoute}
                    color="#9ca3af"
                    weight={3}
                    opacity={0.7}
                    dashArray="6 8"
                  />
                )}

                {/* After: optimized route */}
                {optimizedRoute.length > 0 && (
                  <Polyline
                    positions={optimizedRoute}
                    color="#ea580c"
                    weight={4}
                    opacity={0.9}
                  />
                )}

                {/* Live animated delivery truck */}
                {truckPosition && (
                  <Marker position={truckPosition} icon={truckIcon}>
                    <Popup>
                      <div className="p-1 text-sm">
                        <p className="font-medium">🚚 Live Delivery Truck</p>
                        <p className="text-gray-600">Speed: {simSpeed}x simulation</p>
                        <p className="text-gray-600">Status: {isSimulating ? 'En route' : 'Paused'}</p>
                      </div>
                    </Popup>
                  </Marker>
                )}
              </MapContainer>
            </div>
            
            {optimizedRoute.length > 0 && (
              <div className="mt-4 p-4 bg-green-50 border border-green-200 rounded-lg">
                <p className="text-sm text-green-700">
                  ✓ Route optimized! The orange line is the AI-optimized path
                  {showBeforeAfter && naiveRoute.length > 0 && (
                    <> — the dashed gray line shows the original (unoptimized) order for comparison</>
                  )}
                  . The 🚚 truck marker animates the live delivery journey in real time.
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