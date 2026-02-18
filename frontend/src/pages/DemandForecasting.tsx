import React, { useState } from 'react';
import { Upload, Calendar, Download, TrendingUp, AlertCircle } from 'lucide-react';
import LoadingSpinner from '../components/LoadingSpinner';
import { Line } from 'react-chartjs-2';

const DemandForecasting: React.FC = () => {
  const [isTraining, setIsTraining] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [startDate, setStartDate] = useState('2024-01-01');
  const [endDate, setEndDate] = useState('2024-06-30');
  const [forecastResults, setForecastResults] = useState<any>(null);

  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      setSelectedFile(file);
    }
  };

  const handleTrainModel = async () => {
    setIsTraining(true);
    // Simulate model training
    try {
      await new Promise(resolve => setTimeout(resolve, 3000));
      
      // Simulate forecast results
      setForecastResults({
        accuracy: 95.8,
        rmse: 23.4,
        mae: 18.7,
        predictions: [
          { date: '2024-07-01', predicted: 1420, confidence: 0.92 },
          { date: '2024-07-02', predicted: 1380, confidence: 0.89 },
          { date: '2024-07-03', predicted: 1650, confidence: 0.94 },
          { date: '2024-07-04', predicted: 1590, confidence: 0.91 },
          { date: '2024-07-05', predicted: 1710, confidence: 0.93 },
        ]
      });
    } catch (error) {
      console.error('Training failed:', error);
    } finally {
      setIsTraining(false);
    }
  };

  const forecastData = {
    labels: ['Jul 1', 'Jul 2', 'Jul 3', 'Jul 4', 'Jul 5'],
    datasets: [
      {
        label: 'Predicted Demand',
        data: [1420, 1380, 1650, 1590, 1710],
        borderColor: 'rgb(37, 99, 235)',
        backgroundColor: 'rgba(37, 99, 235, 0.1)',
        tension: 0.4,
      },
      {
        label: 'Confidence Interval',
        data: [1350, 1310, 1580, 1520, 1640],
        borderColor: 'rgba(37, 99, 235, 0.3)',
        backgroundColor: 'rgba(37, 99, 235, 0.05)',
        borderDash: [5, 5],
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
        text: 'Demand Forecast - Next 5 Days',
      },
    },
  };

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="bg-gradient-to-r from-green-600 to-green-800 rounded-xl p-8 text-white">
        <h1 className="text-3xl font-bold mb-2">Demand Forecasting</h1>
        <p className="text-green-100">Use LSTM neural networks to predict future delivery demand</p>
      </div>

      {/* Data Upload Section */}
      <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
        <h2 className="text-xl font-semibold text-gray-800 mb-4">Data Upload & Configuration</h2>
        
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* File Upload */}
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Historical Orders Data (CSV)
              </label>
              <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center hover:border-gray-400 transition-colors">
                <input
                  type="file"
                  accept=".csv"
                  onChange={handleFileUpload}
                  className="hidden"
                  id="file-upload"
                />
                <label htmlFor="file-upload" className="cursor-pointer">
                  <Upload className="h-8 w-8 text-gray-400 mx-auto mb-2" />
                  <p className="text-sm text-gray-600">
                    {selectedFile ? selectedFile.name : 'Click to upload CSV file'}
                  </p>
                </label>
              </div>
            </div>

            {selectedFile && (
              <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                <div className="flex items-center space-x-2">
                  <div className="h-2 w-2 bg-green-400 rounded-full"></div>
                  <p className="text-sm text-green-700">File uploaded successfully</p>
                </div>
                <p className="text-xs text-green-600 mt-1">
                  Ready for model training
                </p>
              </div>
            )}
          </div>

          {/* Date Range */}
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Forecast Period
              </label>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs text-gray-600 mb-1">Start Date</label>
                  <input
                    type="date"
                    value={startDate}
                    onChange={(e) => setStartDate(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500"
                  />
                </div>
                <div>
                  <label className="block text-xs text-gray-600 mb-1">End Date</label>
                  <input
                    type="date"
                    value={endDate}
                    onChange={(e) => setEndDate(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500"
                  />
                </div>
              </div>
            </div>

            <button
              onClick={handleTrainModel}
              disabled={!selectedFile || isTraining}
              className="w-full flex items-center justify-center space-x-2 py-3 px-4 bg-green-600 hover:bg-green-700 disabled:bg-gray-400 text-white rounded-lg transition-colors"
            >
              {isTraining ? (
                <LoadingSpinner size="sm" />
              ) : (
                <>
                  <TrendingUp className="h-5 w-5" />
                  <span>Train LSTM Model & Forecast</span>
                </>
              )}
            </button>
          </div>
        </div>
      </div>

      {/* Training Progress */}
      {isTraining && (
        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
          <div className="flex items-center space-x-4">
            <LoadingSpinner size="md" />
            <div>
              <h3 className="text-lg font-medium text-gray-800">Training LSTM Model</h3>
              <p className="text-sm text-gray-600">Processing historical data and generating forecasts...</p>
            </div>
          </div>
          <div className="mt-4 bg-gray-200 rounded-full h-2">
            <div className="bg-green-600 h-2 rounded-full w-3/4 transition-all duration-1000"></div>
          </div>
          <p className="text-xs text-gray-600 mt-2">Epoch 75/100 - Validation Accuracy: 94.2%</p>
        </div>
      )}

      {/* Results */}
      {forecastResults && (
        <div className="space-y-6">
          {/* Model Performance */}
          <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
            <h3 className="text-lg font-semibold text-gray-800 mb-4">Model Performance</h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="text-center p-4 bg-green-50 rounded-lg">
                <p className="text-2xl font-bold text-green-600">{forecastResults.accuracy}%</p>
                <p className="text-sm text-gray-600">Accuracy</p>
              </div>
              <div className="text-center p-4 bg-blue-50 rounded-lg">
                <p className="text-2xl font-bold text-blue-600">{forecastResults.rmse}</p>
                <p className="text-sm text-gray-600">RMSE</p>
              </div>
              <div className="text-center p-4 bg-orange-50 rounded-lg">
                <p className="text-2xl font-bold text-orange-600">{forecastResults.mae}</p>
                <p className="text-sm text-gray-600">MAE</p>
              </div>
            </div>
          </div>

          {/* Forecast Chart */}
          <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-lg font-semibold text-gray-800">Demand Forecast</h3>
              <button className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors">
                <Download className="h-4 w-4" />
                <span>Export Results</span>
              </button>
            </div>
            <Line data={forecastData} options={chartOptions} />
          </div>

          {/* Predictions Table */}
          <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
            <h3 className="text-lg font-semibold text-gray-800 mb-4">Detailed Predictions</h3>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-gray-200">
                    <th className="text-left py-2 font-medium text-gray-600">Date</th>
                    <th className="text-left py-2 font-medium text-gray-600">Predicted Demand</th>
                    <th className="text-left py-2 font-medium text-gray-600">Confidence</th>
                    <th className="text-left py-2 font-medium text-gray-600">Status</th>
                  </tr>
                </thead>
                <tbody>
                  {forecastResults.predictions.map((pred: any, index: number) => (
                    <tr key={index} className="border-b border-gray-100">
                      <td className="py-3">{pred.date}</td>
                      <td className="py-3 font-medium">{pred.predicted.toLocaleString()}</td>
                      <td className="py-3">
                        <span className={`px-2 py-1 rounded-full text-xs ${
                          pred.confidence > 0.9 
                            ? 'bg-green-100 text-green-700' 
                            : 'bg-yellow-100 text-yellow-700'
                        }`}>
                          {(pred.confidence * 100).toFixed(1)}%
                        </span>
                      </td>
                      <td className="py-3">
                        <div className="flex items-center space-x-1">
                          <div className="h-2 w-2 bg-green-400 rounded-full"></div>
                          <span className="text-xs text-gray-600">Predicted</span>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}

      {/* Help Section */}
      <div className="bg-blue-50 border border-blue-200 rounded-xl p-6">
        <div className="flex items-start space-x-3">
          <AlertCircle className="h-6 w-6 text-blue-600 mt-0.5" />
          <div>
            <h3 className="text-lg font-medium text-blue-800 mb-2">How to Use Demand Forecasting</h3>
            <div className="text-sm text-blue-700 space-y-2">
              <p>1. Upload a CSV file with historical order data (columns: date, quantity, region)</p>
              <p>2. Select the forecast period using the date range selector</p>
              <p>3. Click "Train LSTM Model & Forecast" to generate predictions</p>
              <p>4. Review model performance metrics and export results</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default DemandForecasting;