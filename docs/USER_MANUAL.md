# User Manual - Smart Logistics System

## 📖 Table of Contents
1. [Getting Started](#getting-started)
2. [Dashboard Overview](#dashboard-overview)
3. [Demand Forecasting](#demand-forecasting)
4. [Route Optimization](#route-optimization)
5. [Data Management](#data-management)
6. [Analytics](#analytics)
7. [Troubleshooting](#troubleshooting)

## 🚀 Getting Started

### System Requirements
- **Web Browser**: Chrome 90+, Firefox 88+, Safari 14+, Edge 90+
- **Internet Connection**: Stable broadband connection
- **Screen Resolution**: 1024x768 minimum (1920x1080 recommended)
- **JavaScript**: Must be enabled

### Accessing the System
1. Open your web browser
2. Navigate to the Smart Logistics System URL
3. You'll be redirected to the login page

### Login Credentials
**Demo Account:**
- **Email**: demo@smartlogistics.com
- **Password**: demo123

### First Time Setup
1. Log in with the provided credentials
2. Explore the dashboard to familiarize yourself with the interface
3. Upload sample data to test the system features
4. Review the help tooltips and guided tours

## 📊 Dashboard Overview

### Main Dashboard Features
The dashboard provides a comprehensive overview of your logistics operations with real-time metrics and visualizations.

#### Key Performance Indicators (KPIs)
- **Total Deliveries**: Current month delivery count
- **Cost Savings**: Percentage reduction in operational costs
- **Average Delivery Time**: Mean delivery duration in minutes
- **Route Efficiency**: Optimization effectiveness percentage

#### Interactive Charts
- **Demand Forecasting Chart**: Shows predicted vs actual demand trends
- **Performance Metrics**: Historical performance data
- **Regional Analysis**: Delivery distribution by zones

#### Quick Actions Panel
- **Optimize Routes**: Direct access to route optimization
- **Forecast Demand**: Launch demand prediction module
- **Manage Data**: Access data upload and management tools

### Navigation Menu
- **Dashboard**: Main overview page
- **Demand Forecasting**: AI-powered demand prediction
- **Route Optimization**: Delivery route planning and optimization
- **Data Management**: Upload and manage datasets
- **Analytics**: Detailed performance analysis

## 🔮 Demand Forecasting

### Overview
The Demand Forecasting module uses advanced LSTM neural networks to predict future delivery demand based on historical data.

### Step-by-Step Guide

#### 1. Data Upload
1. Click on **"Demand Forecasting"** in the navigation menu
2. In the **"Data Upload & Configuration"** section:
   - Click **"Choose a file to upload"**
   - Select a CSV file with historical order data
   - Ensure your CSV includes these columns:
     - `order_date` (YYYY-MM-DD format)
     - `quantity` (numeric)
     - `customer_id` (optional)
     - `product_id` (optional)

#### 2. Configure Forecast Period
1. Set the **Start Date** for historical data analysis
2. Set the **End Date** for the forecast period
3. The system will use data between these dates for training

#### 3. Train the Model
1. Click **"Train LSTM Model & Forecast"**
2. Wait for the training process to complete (typically 1-3 minutes)
3. Monitor the progress bar and training metrics

#### 4. Review Results
Once training is complete, you'll see:
- **Model Performance Metrics**:
  - Accuracy percentage
  - RMSE (Root Mean Square Error)
  - MAE (Mean Absolute Error)
- **Forecast Chart**: Visual representation of predictions
- **Detailed Predictions Table**: Day-by-day forecasts with confidence levels

#### 5. Export Results
- Click **"Export Results"** to download predictions as CSV
- Use the data for inventory planning and resource allocation

### Best Practices
- **Data Quality**: Ensure consistent, clean historical data
- **Data Volume**: Use at least 30 days of historical data for better accuracy
- **Regular Updates**: Retrain models monthly with new data
- **Validation**: Compare predictions with actual results to assess accuracy

## 🗺️ Route Optimization

### Overview
The Route Optimization module helps you create the most efficient delivery routes using advanced algorithms.

### Step-by-Step Guide

#### 1. Access Route Optimization
1. Click **"Route Optimization"** in the navigation menu
2. You'll see an interactive map with existing delivery points

#### 2. Configure Optimization Settings
In the **"Optimization Settings"** panel:
- **Algorithm**: Choose between OR-Tools (TSP/VRP) or Genetic Algorithm
- **Vehicle Capacity**: Set maximum load capacity
- **Time Windows**: Configure delivery time constraints (if applicable)

#### 3. Manage Delivery Points
**Adding New Points:**
1. Enter an address in the **"Add Delivery Point"** section
2. Click **"Add Point"** to include it in the route
3. The point will appear on the map with a marker

**Removing Points:**
1. In the **"Delivery Points"** list, click the trash icon next to any point
2. The point will be removed from both the list and map

**Point Properties:**
- **Priority**: High, Medium, or Low delivery priority
- **Time Window**: Preferred delivery time slots
- **Zone**: Delivery area classification

#### 4. Optimize the Route
1. Ensure you have at least 2 delivery points
2. Click **"Optimize Route"**
3. Wait for the algorithm to calculate the optimal path (typically 10-30 seconds)

#### 5. Review Optimization Results
After optimization, you'll see:
- **Route Visualization**: Orange line showing the optimized path on the map
- **Route Metrics**:
  - Total Distance (in kilometers)
  - Estimated Time (in minutes)
  - Fuel Savings percentage
  - Cost Savings percentage
- **Algorithm Used**: Which optimization method was applied

#### 6. Export Route Data
- Click **"Export"** in the Route Metrics panel
- Download route details as CSV or PDF for drivers

### Map Features
- **Zoom Controls**: Use mouse wheel or +/- buttons
- **Pan**: Click and drag to move around the map
- **Markers**: Click on delivery points for detailed information
- **Route Line**: Orange line shows the optimized delivery sequence

### Optimization Tips
- **Point Density**: Group nearby deliveries for better efficiency
- **Time Windows**: Use realistic time constraints
- **Vehicle Capacity**: Set accurate capacity limits
- **Priority Levels**: Mark urgent deliveries as high priority

## 📁 Data Management

### Overview
The Data Management module allows you to upload, validate, and manage your logistics datasets.

### Supported File Formats
- **CSV**: Comma-separated values (recommended)
- **Excel**: .xlsx files
- **JSON**: JavaScript Object Notation

### Step-by-Step Guide

#### 1. Upload New Dataset
1. Navigate to **"Data Management"**
2. In the **"Upload New Dataset"** section:
   - Drag and drop a file or click **"Choose a file to upload"**
   - Select your data file
   - Review the file information displayed

#### 2. Data Validation
1. Click **"Upload & Validate"**
2. The system will check:
   - File format compatibility
   - Required column presence
   - Data type validation
   - Missing value detection

#### 3. Review Validation Results
You'll see:
- **Validation Status**: Valid/Invalid with details
- **Records Count**: Number of data rows processed
- **Column Mapping**: Which columns were found vs required
- **Warnings**: Any data quality issues

#### 4. Manage Existing Datasets
In the **"Uploaded Datasets"** table:
- **Preview**: Click the eye icon to view data samples
- **Download**: Click the download icon to export data
- **Delete**: Click the trash icon to remove datasets

### Required Data Formats

#### Orders Dataset
```csv
order_id,order_date,customer_id,quantity,latitude,longitude,delivery_address
ORD001,2024-01-15,CUST123,5,40.7128,-74.0060,"123 Main St, NYC"
```

#### Locations Dataset
```csv
location_id,address,latitude,longitude,zone,priority
LOC001,"Central Park, NYC",40.7829,-73.9654,A,High
```

### Sample Data
- Click **"Download Sample Data"** to get template files
- Use these templates to format your own data correctly
- Sample files include realistic logistics data for testing

### Data Quality Tips
- **Consistent Formatting**: Use standard date formats (YYYY-MM-DD)
- **Complete Records**: Avoid missing critical fields
- **Accurate Coordinates**: Verify latitude/longitude values
- **Clean Data**: Remove duplicates and invalid entries

## 📈 Analytics

### Overview
The Analytics module provides comprehensive insights into your logistics performance with detailed charts and metrics.

### Key Analytics Sections

#### 1. Performance Summary
- **Total Cost Savings**: Cumulative savings from optimization
- **Average Delivery Time**: Mean delivery duration trends
- **Route Efficiency**: Overall optimization effectiveness
- **Fuel Savings**: Environmental and cost impact

#### 2. Cost Analysis
- **Before vs After Optimization**: Monthly cost comparison charts
- **Savings Breakdown**: Detailed cost reduction analysis
- **ROI Calculation**: Return on investment metrics

#### 3. Delivery Performance
- **Weekly Performance**: Daily delivery statistics
- **On-time Delivery Rate**: Punctuality metrics
- **Regional Distribution**: Performance by delivery zones

#### 4. Efficiency Trends
- **Route Optimization**: Historical efficiency improvements
- **Time Savings**: Delivery time reduction trends
- **Resource Utilization**: Vehicle and driver efficiency

### Using Analytics

#### 1. Time Range Selection
- Use the dropdown to select analysis period:
  - Last 7 Days
  - Last 30 Days
  - Last 90 Days
  - Last Year

#### 2. Export Reports
1. Click **"Export Report"** in the top-right corner
2. Choose format (PDF, Excel, CSV)
3. Download comprehensive analytics report

#### 3. Interactive Charts
- **Hover**: View detailed data points
- **Zoom**: Click and drag to zoom into specific periods
- **Legend**: Click legend items to show/hide data series

### Key Metrics Explained

#### Cost Savings
- **Fuel Costs**: Reduction in fuel expenses through shorter routes
- **Labor Costs**: Time savings translated to labor cost reduction
- **Vehicle Maintenance**: Reduced wear and tear from optimized routes

#### Efficiency Metrics
- **Route Efficiency**: Percentage improvement over baseline routes
- **Time Efficiency**: Delivery time reduction percentage
- **Resource Utilization**: Vehicle capacity and driver time optimization

#### Performance Indicators
- **On-time Delivery**: Percentage of deliveries within time windows
- **Customer Satisfaction**: Derived from delivery performance
- **Operational Excellence**: Overall system effectiveness score

## 🔧 Troubleshooting

### Common Issues and Solutions

#### Login Problems
**Issue**: Cannot log in with provided credentials
**Solution**:
1. Verify you're using: demo@smartlogistics.com / demo123
2. Check for caps lock or extra spaces
3. Clear browser cache and cookies
4. Try a different browser

#### File Upload Issues
**Issue**: CSV file upload fails
**Solution**:
1. Check file format (must be .csv, .xlsx, or .json)
2. Verify file size (maximum 10MB)
3. Ensure required columns are present
4. Remove special characters from file name

#### Map Not Loading
**Issue**: Route optimization map doesn't display
**Solution**:
1. Check internet connection
2. Disable ad blockers temporarily
3. Enable JavaScript in browser settings
4. Try refreshing the page

#### Slow Performance
**Issue**: System responds slowly
**Solution**:
1. Check internet connection speed
2. Close unnecessary browser tabs
3. Clear browser cache
4. Use recommended browsers (Chrome, Firefox)

#### Model Training Fails
**Issue**: LSTM model training doesn't complete
**Solution**:
1. Verify data has at least 30 rows
2. Check for missing values in quantity column
3. Ensure date format is YYYY-MM-DD
4. Try with sample data first

### Getting Help

#### In-App Help
- Look for **?** icons throughout the interface
- Hover over elements for helpful tooltips
- Check the help sections in each module

#### Technical Support
- Document the exact error message
- Note which browser and version you're using
- Describe the steps that led to the issue
- Include screenshots if helpful

#### Best Practices
- **Regular Backups**: Export important data regularly
- **Browser Updates**: Keep your browser updated
- **Data Validation**: Always validate data before processing
- **System Monitoring**: Check performance metrics regularly

### System Limitations
- **File Size**: Maximum 10MB per upload
- **Concurrent Users**: Optimal performance with <100 simultaneous users
- **Data Points**: Route optimization works best with <100 delivery points
- **Browser Support**: Modern browsers only (IE not supported)

---

*For additional support or questions not covered in this manual, please contact your system administrator or technical support team.*