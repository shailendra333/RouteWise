import React, { useState } from 'react';
import { Upload, Download, Eye, Trash2, FileText, Database, CheckCircle, AlertCircle } from 'lucide-react';
import LoadingSpinner from '../components/LoadingSpinner';

interface DataFile {
  id: number;
  name: string;
  type: 'orders' | 'locations' | 'routes';
  size: string;
  uploadDate: string;
  status: 'valid' | 'invalid' | 'processing';
  records: number;
}

const DataManagement: React.FC = () => {
  const [files, setFiles] = useState<DataFile[]>([
    { id: 1, name: 'historical_orders_2024.csv', type: 'orders', size: '2.1 MB', uploadDate: '2024-01-15', status: 'valid', records: 12547 },
    { id: 2, name: 'delivery_locations.csv', type: 'locations', size: '850 KB', uploadDate: '2024-01-14', status: 'valid', records: 3421 },
    { id: 3, name: 'optimized_routes_jan.csv', type: 'routes', size: '1.2 MB', uploadDate: '2024-01-13', status: 'valid', records: 892 },
  ]);

  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [previewData, setPreviewData] = useState<any>(null);
  const [validationResults, setValidationResults] = useState<any>(null);

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      setSelectedFile(file);
      setPreviewData(null);
      setValidationResults(null);
    }
  };

  const handleUpload = async () => {
    if (!selectedFile) return;
    
    setUploading(true);
    try {
      // Simulate file upload and validation
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      // Simulate validation results
      setValidationResults({
        isValid: true,
        records: Math.floor(Math.random() * 10000) + 1000,
        errors: [],
        warnings: ['Some records have missing postal codes'],
        requiredColumns: ['order_id', 'date', 'customer_id', 'quantity'],
        foundColumns: ['order_id', 'date', 'customer_id', 'quantity', 'location']
      });

      // Add to files list
      const newFile: DataFile = {
        id: Date.now(),
        name: selectedFile.name,
        type: 'orders',
        size: `${(selectedFile.size / 1024 / 1024).toFixed(1)} MB`,
        uploadDate: new Date().toISOString().split('T')[0],
        status: 'valid',
        records: Math.floor(Math.random() * 10000) + 1000
      };
      
      setFiles([newFile, ...files]);
      setSelectedFile(null);
    } catch (error) {
      console.error('Upload failed:', error);
    } finally {
      setUploading(false);
    }
  };

  const handlePreview = (file: DataFile) => {
    // Simulate data preview
    const sampleData = [
      { order_id: 'ORD001', date: '2024-01-15', customer_id: 'CUST123', quantity: 5, location: 'New York' },
      { order_id: 'ORD002', date: '2024-01-15', customer_id: 'CUST124', quantity: 3, location: 'Boston' },
      { order_id: 'ORD003', date: '2024-01-15', customer_id: 'CUST125', quantity: 7, location: 'Chicago' },
    ];
    setPreviewData({ fileName: file.name, data: sampleData });
  };

  const handleDelete = (id: number) => {
    setFiles(files.filter(file => file.id !== id));
  };

  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'orders': return <FileText className="h-5 w-5 text-blue-600" />;
      case 'locations': return <Database className="h-5 w-5 text-green-600" />;
      case 'routes': return <FileText className="h-5 w-5 text-orange-600" />;
      default: return <FileText className="h-5 w-5 text-gray-600" />;
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'valid': return <CheckCircle className="h-5 w-5 text-green-600" />;
      case 'invalid': return <AlertCircle className="h-5 w-5 text-red-600" />;
      case 'processing': return <div className="w-5 h-5"><LoadingSpinner size="sm" /></div>;
      default: return null;
    }
  };

  const exportSampleData = () => {
    const sampleData = `order_id,date,customer_id,quantity,latitude,longitude,delivery_address
ORD001,2024-01-15,CUST123,5,40.7128,-74.0060,"123 Main St, NYC"
ORD002,2024-01-15,CUST124,3,40.7589,-73.9851,"456 Broadway, NYC"
ORD003,2024-01-15,CUST125,7,40.7614,-73.9776,"789 5th Ave, NYC"`;
    
    const blob = new Blob([sampleData], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'sample_orders_data.csv';
    a.click();
    window.URL.revokeObjectURL(url);
  };

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="bg-gradient-to-r from-purple-600 to-purple-800 rounded-xl p-8 text-white">
        <h1 className="text-3xl font-bold mb-2">Data Management</h1>
        <p className="text-purple-100">Upload, validate, and manage your logistics datasets</p>
      </div>

      {/* Upload Section */}
      <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
        <h2 className="text-xl font-semibold text-gray-800 mb-4">Upload New Dataset</h2>
        
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* File Upload */}
          <div className="space-y-4">
            <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center hover:border-gray-400 transition-colors">
              <input
                type="file"
                accept=".csv,.xlsx,.json"
                onChange={handleFileSelect}
                className="hidden"
                id="file-upload"
              />
              <label htmlFor="file-upload" className="cursor-pointer">
                <Upload className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                <p className="text-lg font-medium text-gray-700">
                  {selectedFile ? selectedFile.name : 'Choose a file to upload'}
                </p>
                <p className="text-sm text-gray-500 mt-2">
                  Supports CSV, Excel, and JSON formats
                </p>
              </label>
            </div>

            {selectedFile && (
              <div className="space-y-3">
                <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                  <div className="flex items-center space-x-3">
                    <FileText className="h-6 w-6 text-blue-600" />
                    <div>
                      <p className="font-medium text-blue-800">{selectedFile.name}</p>
                      <p className="text-sm text-blue-600">
                        {(selectedFile.size / 1024 / 1024).toFixed(2)} MB
                      </p>
                    </div>
                  </div>
                </div>

                <button
                  onClick={handleUpload}
                  disabled={uploading}
                  className="w-full flex items-center justify-center space-x-2 py-3 px-4 bg-purple-600 hover:bg-purple-700 disabled:bg-gray-400 text-white rounded-lg transition-colors"
                >
                  {uploading ? (
                    <LoadingSpinner size="sm" />
                  ) : (
                    <>
                      <Upload className="h-5 w-5" />
                      <span>Upload & Validate</span>
                    </>
                  )}
                </button>
              </div>
            )}
          </div>

          {/* Sample Data */}
          <div className="space-y-4">
            <h3 className="text-lg font-medium text-gray-800">Need Sample Data?</h3>
            <p className="text-sm text-gray-600">
              Download sample datasets to get started with the platform
            </p>
            
            <div className="space-y-2">
              <button
                onClick={exportSampleData}
                className="w-full flex items-center justify-between p-3 bg-gray-50 hover:bg-gray-100 rounded-lg transition-colors"
              >
                <div className="flex items-center space-x-3">
                  <FileText className="h-5 w-5 text-blue-600" />
                  <div className="text-left">
                    <p className="font-medium text-gray-800">Sample Orders Data</p>
                    <p className="text-sm text-gray-600">Historical order records with locations</p>
                  </div>
                </div>
                <Download className="h-5 w-5 text-gray-600" />
              </button>
              
              <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                <h4 className="font-medium text-yellow-800 mb-2">Required CSV Columns:</h4>
                <div className="text-sm text-yellow-700 space-y-1">
                  <p>• <strong>order_id:</strong> Unique order identifier</p>
                  <p>• <strong>date:</strong> Order date (YYYY-MM-DD)</p>
                  <p>• <strong>customer_id:</strong> Customer identifier</p>
                  <p>• <strong>quantity:</strong> Order quantity</p>
                  <p>• <strong>latitude, longitude:</strong> Delivery coordinates</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Validation Results */}
      {validationResults && (
        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
          <h3 className="text-lg font-semibold text-gray-800 mb-4">Validation Results</h3>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
            <div className="text-center p-4 bg-green-50 rounded-lg">
              <CheckCircle className="h-8 w-8 text-green-600 mx-auto mb-2" />
              <p className="font-medium text-green-800">Valid Dataset</p>
              <p className="text-sm text-green-600">{validationResults.records} records found</p>
            </div>
            <div className="text-center p-4 bg-blue-50 rounded-lg">
              <Database className="h-8 w-8 text-blue-600 mx-auto mb-2" />
              <p className="font-medium text-blue-800">Columns Matched</p>
              <p className="text-sm text-blue-600">{validationResults.foundColumns.length}/{validationResults.requiredColumns.length}</p>
            </div>
            <div className="text-center p-4 bg-orange-50 rounded-lg">
              <AlertCircle className="h-8 w-8 text-orange-600 mx-auto mb-2" />
              <p className="font-medium text-orange-800">Warnings</p>
              <p className="text-sm text-orange-600">{validationResults.warnings.length} issues</p>
            </div>
          </div>

          {validationResults.warnings.length > 0 && (
            <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
              <h4 className="font-medium text-yellow-800 mb-2">Warnings:</h4>
              <ul className="text-sm text-yellow-700 space-y-1">
                {validationResults.warnings.map((warning: string, index: number) => (
                  <li key={index}>• {warning}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}

      {/* Files List */}
      <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-lg font-semibold text-gray-800">Uploaded Datasets ({files.length})</h3>
          <button className="flex items-center space-x-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors">
            <Download className="h-4 w-4" />
            <span>Export All</span>
          </button>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-gray-200">
                <th className="text-left py-3 font-medium text-gray-600">File</th>
                <th className="text-left py-3 font-medium text-gray-600">Type</th>
                <th className="text-left py-3 font-medium text-gray-600">Size</th>
                <th className="text-left py-3 font-medium text-gray-600">Records</th>
                <th className="text-left py-3 font-medium text-gray-600">Upload Date</th>
                <th className="text-left py-3 font-medium text-gray-600">Status</th>
                <th className="text-left py-3 font-medium text-gray-600">Actions</th>
              </tr>
            </thead>
            <tbody>
              {files.map((file) => (
                <tr key={file.id} className="border-b border-gray-100 hover:bg-gray-50">
                  <td className="py-4">
                    <div className="flex items-center space-x-3">
                      {getTypeIcon(file.type)}
                      <span className="font-medium text-gray-800">{file.name}</span>
                    </div>
                  </td>
                  <td className="py-4">
                    <span className="px-2 py-1 bg-gray-100 text-gray-700 rounded-full text-xs capitalize">
                      {file.type}
                    </span>
                  </td>
                  <td className="py-4 text-gray-600">{file.size}</td>
                  <td className="py-4 text-gray-600">{file.records.toLocaleString()}</td>
                  <td className="py-4 text-gray-600">{file.uploadDate}</td>
                  <td className="py-4">
                    <div className="flex items-center space-x-2">
                      {getStatusIcon(file.status)}
                      <span className={`text-xs capitalize ${
                        file.status === 'valid' ? 'text-green-600' : 
                        file.status === 'invalid' ? 'text-red-600' : 'text-yellow-600'
                      }`}>
                        {file.status}
                      </span>
                    </div>
                  </td>
                  <td className="py-4">
                    <div className="flex items-center space-x-2">
                      <button
                        onClick={() => handlePreview(file)}
                        className="p-1 text-blue-600 hover:text-blue-800 transition-colors"
                        title="Preview"
                      >
                        <Eye className="h-4 w-4" />
                      </button>
                      <button
                        className="p-1 text-green-600 hover:text-green-800 transition-colors"
                        title="Download"
                      >
                        <Download className="h-4 w-4" />
                      </button>
                      <button
                        onClick={() => handleDelete(file.id)}
                        className="p-1 text-red-600 hover:text-red-800 transition-colors"
                        title="Delete"
                      >
                        <Trash2 className="h-4 w-4" />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Data Preview */}
      {previewData && (
        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
          <h3 className="text-lg font-semibold text-gray-800 mb-4">Data Preview: {previewData.fileName}</h3>
          <div className="overflow-x-auto">
            <table className="w-full text-sm border border-gray-200">
              <thead>
                <tr className="bg-gray-50">
                  {Object.keys(previewData.data[0]).map((key) => (
                    <th key={key} className="text-left py-2 px-4 font-medium text-gray-600 border-b">
                      {key}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {previewData.data.map((row: any, index: number) => (
                  <tr key={index} className="border-b border-gray-100">
                    {Object.values(row).map((value: any, cellIndex: number) => (
                      <td key={cellIndex} className="py-2 px-4 text-gray-600">
                        {value}
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <p className="text-sm text-gray-500 mt-4">Showing first 3 rows of data</p>
        </div>
      )}
    </div>
  );
};

export default DataManagement;