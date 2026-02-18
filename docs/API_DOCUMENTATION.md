# API Documentation - Smart Logistics System

## 📋 Table of Contents
1. [Overview](#overview)
2. [Authentication](#authentication)
3. [Data Management Endpoints](#data-management-endpoints)
4. [Demand Forecasting Endpoints](#demand-forecasting-endpoints)
5. [Route Optimization Endpoints](#route-optimization-endpoints)
6. [Analytics Endpoints](#analytics-endpoints)
7. [Error Handling](#error-handling)
8. [Rate Limiting](#rate-limiting)

## 🌐 Overview

### Base URL
```
Development: http://localhost:5000
Production: https://your-api-domain.com
```

### API Version
Current version: `v1`

### Content Type
All requests and responses use `application/json` content type unless specified otherwise.

### Response Format
All API responses follow this standard format:
```json
{
  "success": true,
  "data": {},
  "message": "Operation completed successfully",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

## 🔐 Authentication

### Login
Authenticate user and receive session token.

**Endpoint:** `POST /api/auth/login`

**Request Body:**
```json
{
  "email": "demo@smartlogistics.com",
  "password": "demo123"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "user": {
      "id": 1,
      "email": "demo@smartlogistics.com",
      "name": "Demo User"
    },
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "expires_at": "2024-01-16T10:30:00Z"
  },
  "message": "Login successful"
}
```

### Logout
Invalidate current session.

**Endpoint:** `POST /api/auth/logout`

**Headers:**
```
Authorization: Bearer <token>
```

**Response:**
```json
{
  "success": true,
  "message": "Logout successful"
}
```

### Profile
Get current user profile information.

**Endpoint:** `GET /api/auth/profile`

**Headers:**
```
Authorization: Bearer <token>
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": 1,
    "email": "demo@smartlogistics.com",
    "name": "Demo User",
    "created_at": "2024-01-01T00:00:00Z",
    "last_login": "2024-01-15T10:30:00Z"
  }
}
```

## 📊 Data Management Endpoints

### Upload Data
Upload CSV, Excel, or JSON files for processing.

**Endpoint:** `POST /api/upload-data`

**Headers:**
```
Authorization: Bearer <token>
Content-Type: multipart/form-data
```

**Request Body:**
```
file: <binary_file_data>
data_type: "orders" | "locations" | "routes"
```

**Response:**
```json
{
  "success": true,
  "data": {
    "file_id": "uuid-string",
    "filename": "orders_data.csv",
    "records_processed": 1250,
    "columns_found": ["order_id", "date", "quantity", "latitude", "longitude"],
    "validation_status": "valid",
    "warnings": ["Some records have missing postal codes"]
  },
  "message": "File uploaded and processed successfully"
}
```

### Data Preview
Get a preview of uploaded data.

**Endpoint:** `GET /api/data-preview`

**Query Parameters:**
- `file_id` (string): File identifier
- `limit` (integer, optional): Number of records to return (default: 10)
- `offset` (integer, optional): Number of records to skip (default: 0)

**Response:**
```json
{
  "success": true,
  "data": {
    "records": [
      {
        "order_id": "ORD001",
        "order_date": "2024-01-15",
        "customer_id": "CUST123",
        "quantity": 5,
        "latitude": 40.7128,
        "longitude": -74.0060
      }
    ],
    "total_records": 1250,
    "columns": ["order_id", "order_date", "customer_id", "quantity", "latitude", "longitude"]
  }
}
```

### Validate Data
Validate uploaded data format and quality.

**Endpoint:** `POST /api/validate-data`

**Request Body:**
```json
{
  "file_id": "uuid-string",
  "data_type": "orders",
  "validation_rules": {
    "required_columns": ["order_id", "date", "quantity"],
    "date_format": "YYYY-MM-DD",
    "numeric_columns": ["quantity", "latitude", "longitude"]
  }
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "is_valid": true,
    "validation_results": {
      "missing_columns": [],
      "invalid_dates": 0,
      "invalid_numbers": 0,
      "duplicate_records": 5,
      "null_values": {
        "quantity": 0,
        "latitude": 2,
        "longitude": 2
      }
    },
    "recommendations": [
      "Consider filling missing coordinate values",
      "Remove duplicate order IDs"
    ]
  }
}
```

### Export Data
Export processed data in various formats.

**Endpoint:** `GET /api/data-export`

**Query Parameters:**
- `file_id` (string): File identifier
- `format` (string): Export format ("csv", "excel", "json")
- `include_processed` (boolean): Include processed/cleaned data

**Response:**
```
Content-Type: application/octet-stream
Content-Disposition: attachment; filename="exported_data.csv"

<binary_file_data>
```

## 🔮 Demand Forecasting Endpoints

### Train Forecast Model
Train LSTM model with historical data.

**Endpoint:** `POST /api/train-forecast-model`

**Request Body:**
```json
{
  "data_source": "file_id_or_database",
  "file_id": "uuid-string",
  "model_parameters": {
    "sequence_length": 30,
    "prediction_horizon": 7,
    "epochs": 100,
    "batch_size": 32,
    "learning_rate": 0.001
  },
  "features": ["demand", "day_of_week", "month", "seasonality"],
  "date_range": {
    "start_date": "2024-01-01",
    "end_date": "2024-06-30"
  }
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "model_id": "model-uuid",
    "training_results": {
      "epochs_completed": 85,
      "final_loss": 0.0234,
      "validation_loss": 0.0267,
      "training_time": 180.5,
      "model_size": "2.3MB"
    },
    "performance_metrics": {
      "rmse": 23.4,
      "mae": 18.7,
      "mape": 12.3,
      "r2_score": 0.94
    }
  },
  "message": "Model trained successfully"
}
```

### Generate Predictions
Generate demand forecasts using trained model.

**Endpoint:** `POST /api/predict-demand`

**Request Body:**
```json
{
  "model_id": "model-uuid",
  "prediction_parameters": {
    "days_ahead": 7,
    "confidence_level": 0.95,
    "include_confidence_intervals": true
  },
  "input_data": {
    "start_date": "2024-07-01",
    "historical_context": 30
  }
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "predictions": [
      {
        "date": "2024-07-01",
        "predicted_demand": 1420.5,
        "confidence": 0.92,
        "lower_bound": 1350.2,
        "upper_bound": 1490.8
      },
      {
        "date": "2024-07-02",
        "predicted_demand": 1380.3,
        "confidence": 0.89,
        "lower_bound": 1305.1,
        "upper_bound": 1455.5
      }
    ],
    "model_metrics": {
      "model_version": "v1.2",
      "prediction_accuracy": 94.2,
      "confidence_score": 0.91
    },
    "metadata": {
      "prediction_date": "2024-06-30T15:30:00Z",
      "model_last_trained": "2024-06-29T10:00:00Z"
    }
  }
}
```

### Forecast Accuracy
Get model performance metrics and accuracy statistics.

**Endpoint:** `GET /api/forecast-accuracy`

**Query Parameters:**
- `model_id` (string): Model identifier
- `date_range` (string, optional): Date range for accuracy calculation

**Response:**
```json
{
  "success": true,
  "data": {
    "overall_accuracy": 94.2,
    "metrics": {
      "rmse": 23.4,
      "mae": 18.7,
      "mape": 12.3,
      "directional_accuracy": 87.5
    },
    "accuracy_by_horizon": [
      {"days_ahead": 1, "accuracy": 96.8},
      {"days_ahead": 3, "accuracy": 94.2},
      {"days_ahead": 7, "accuracy": 89.1}
    ],
    "model_performance": {
      "training_samples": 1250,
      "validation_samples": 312,
      "test_samples": 156,
      "last_updated": "2024-06-29T10:00:00Z"
    }
  }
}
```

## 🗺️ Route Optimization Endpoints

### Optimize Routes
Calculate optimal delivery routes using specified algorithm.

**Endpoint:** `POST /api/optimize-routes`

**Request Body:**
```json
{
  "delivery_points": [
    {
      "id": "point_1",
      "address": "123 Main St, NYC",
      "coordinates": [40.7128, -74.0060],
      "priority": "high",
      "time_window": "09:00-11:00",
      "service_time": 15
    },
    {
      "id": "point_2",
      "address": "456 Broadway, NYC",
      "coordinates": [40.7589, -73.9851],
      "priority": "medium",
      "time_window": "11:00-13:00",
      "service_time": 10
    }
  ],
  "vehicles": [
    {
      "id": "vehicle_1",
      "capacity": 100,
      "start_location": [40.7614, -73.9776],
      "end_location": [40.7614, -73.9776]
    }
  ],
  "optimization_parameters": {
    "algorithm": "or-tools",
    "objective": "minimize_distance",
    "max_route_duration": 480,
    "include_traffic": true
  }
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "optimized_routes": [
      {
        "vehicle_id": "vehicle_1",
        "route_sequence": ["depot", "point_1", "point_2", "depot"],
        "total_distance": 12.8,
        "total_time": 45,
        "coordinates": [
          [40.7614, -73.9776],
          [40.7128, -74.0060],
          [40.7589, -73.9851],
          [40.7614, -73.9776]
        ]
      }
    ],
    "optimization_results": {
      "algorithm_used": "or-tools",
      "computation_time": 2.3,
      "total_distance": 12.8,
      "total_time": 45,
      "cost_savings": 23.5,
      "fuel_savings": 18.7
    },
    "comparison": {
      "original_distance": 16.7,
      "optimized_distance": 12.8,
      "improvement": 23.4
    }
  }
}
```

### Route Comparison
Compare different optimization algorithms or parameters.

**Endpoint:** `GET /api/route-comparison`

**Query Parameters:**
- `route_id_1` (string): First route identifier
- `route_id_2` (string): Second route identifier
- `metrics` (array): Metrics to compare

**Response:**
```json
{
  "success": true,
  "data": {
    "comparison_results": {
      "route_1": {
        "algorithm": "genetic",
        "total_distance": 13.2,
        "total_time": 48,
        "fuel_cost": 45.60,
        "efficiency_score": 87.3
      },
      "route_2": {
        "algorithm": "or-tools",
        "total_distance": 12.8,
        "total_time": 45,
        "fuel_cost": 44.20,
        "efficiency_score": 89.1
      }
    },
    "winner": "route_2",
    "improvements": {
      "distance": 3.0,
      "time": 6.3,
      "cost": 3.1,
      "efficiency": 2.1
    }
  }
}
```

### Performance Metrics
Get route optimization performance statistics.

**Endpoint:** `GET /api/performance-metrics`

**Query Parameters:**
- `date_range` (string, optional): Date range for metrics
- `vehicle_id` (string, optional): Specific vehicle metrics

**Response:**
```json
{
  "success": true,
  "data": {
    "overall_metrics": {
      "total_routes_optimized": 156,
      "average_improvement": 23.7,
      "total_distance_saved": 1247.3,
      "total_time_saved": 892.5,
      "cost_savings": 15420.75
    },
    "efficiency_metrics": {
      "route_efficiency": 94.2,
      "fuel_efficiency": 87.8,
      "time_efficiency": 91.5,
      "vehicle_utilization": 89.3
    },
    "algorithm_performance": {
      "or-tools": {
        "usage_count": 89,
        "average_improvement": 25.1,
        "average_computation_time": 2.1
      },
      "genetic": {
        "usage_count": 67,
        "average_improvement": 21.8,
        "average_computation_time": 8.7
      }
    }
  }
}
```

## 📈 Analytics Endpoints

### Analytics Data
Get comprehensive analytics and performance data.

**Endpoint:** `GET /api/analytics-data`

**Query Parameters:**
- `time_range` (string): Time period ("7d", "30d", "90d", "1y")
- `metrics` (array, optional): Specific metrics to include
- `granularity` (string, optional): Data granularity ("daily", "weekly", "monthly")

**Response:**
```json
{
  "success": true,
  "data": {
    "summary_metrics": {
      "total_deliveries": 2847,
      "cost_savings_percentage": 23.5,
      "efficiency_improvement": 18.7,
      "customer_satisfaction": 4.6
    },
    "time_series_data": {
      "daily_deliveries": [
        {"date": "2024-01-01", "deliveries": 245, "on_time": 234},
        {"date": "2024-01-02", "deliveries": 267, "on_time": 251}
      ],
      "cost_analysis": [
        {"month": "Jan", "before": 45000, "after": 32000, "savings": 13000},
        {"month": "Feb", "before": 48000, "after": 34000, "savings": 14000}
      ]
    },
    "regional_analysis": {
      "zone_a": {"deliveries": 892, "efficiency": 94.2},
      "zone_b": {"deliveries": 756, "efficiency": 91.8},
      "zone_c": {"deliveries": 634, "efficiency": 89.5}
    }
  }
}
```

### Cost Analysis
Get detailed cost analysis and savings breakdown.

**Endpoint:** `GET /api/cost-analysis`

**Query Parameters:**
- `time_range` (string): Analysis period
- `cost_categories` (array, optional): Specific cost categories

**Response:**
```json
{
  "success": true,
  "data": {
    "total_savings": {
      "amount": 125420.75,
      "percentage": 23.5,
      "period": "last_6_months"
    },
    "savings_breakdown": {
      "fuel_costs": {
        "before": 45000,
        "after": 36750,
        "savings": 8250,
        "percentage": 18.3
      },
      "labor_costs": {
        "before": 78000,
        "after": 65520,
        "savings": 12480,
        "percentage": 16.0
      },
      "vehicle_maintenance": {
        "before": 23000,
        "after": 19550,
        "savings": 3450,
        "percentage": 15.0
      }
    },
    "roi_analysis": {
      "investment": 50000,
      "total_savings": 125420.75,
      "roi_percentage": 150.8,
      "payback_period_months": 4.8
    }
  }
}
```

### Export Reports
Export analytics reports in various formats.

**Endpoint:** `POST /api/export-reports`

**Request Body:**
```json
{
  "report_type": "comprehensive",
  "format": "pdf",
  "time_range": "30d",
  "include_charts": true,
  "sections": ["summary", "cost_analysis", "performance", "forecasts"]
}
```

**Response:**
```
Content-Type: application/pdf
Content-Disposition: attachment; filename="analytics_report_2024-01-15.pdf"

<binary_pdf_data>
```

## ❌ Error Handling

### Error Response Format
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input data",
    "details": {
      "field": "email",
      "reason": "Invalid email format"
    }
  },
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### Common Error Codes

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `AUTHENTICATION_REQUIRED` | 401 | Authentication token required |
| `INVALID_CREDENTIALS` | 401 | Invalid username or password |
| `ACCESS_DENIED` | 403 | Insufficient permissions |
| `RESOURCE_NOT_FOUND` | 404 | Requested resource not found |
| `VALIDATION_ERROR` | 400 | Input validation failed |
| `FILE_TOO_LARGE` | 413 | Uploaded file exceeds size limit |
| `UNSUPPORTED_FORMAT` | 415 | Unsupported file format |
| `RATE_LIMIT_EXCEEDED` | 429 | Too many requests |
| `INTERNAL_ERROR` | 500 | Internal server error |
| `SERVICE_UNAVAILABLE` | 503 | Service temporarily unavailable |

### Error Examples

#### Validation Error
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Required fields missing",
    "details": {
      "missing_fields": ["email", "password"],
      "invalid_fields": {
        "quantity": "Must be a positive number"
      }
    }
  }
}
```

#### Authentication Error
```json
{
  "success": false,
  "error": {
    "code": "AUTHENTICATION_REQUIRED",
    "message": "Valid authentication token required",
    "details": {
      "token_status": "expired",
      "expires_at": "2024-01-15T09:30:00Z"
    }
  }
}
```

## 🚦 Rate Limiting

### Rate Limits
- **Authentication endpoints**: 5 requests per minute
- **Data upload endpoints**: 10 requests per hour
- **General API endpoints**: 100 requests per minute
- **Analytics endpoints**: 50 requests per minute

### Rate Limit Headers
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1642248600
```

### Rate Limit Exceeded Response
```json
{
  "success": false,
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "Rate limit exceeded",
    "details": {
      "limit": 100,
      "window": "1 minute",
      "retry_after": 45
    }
  }
}
```

---

*This API documentation provides comprehensive information for integrating with the Smart Logistics System. For additional support or questions, please contact the development team.*