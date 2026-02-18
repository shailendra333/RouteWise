# Testing Guide - Smart Logistics System

## 📋 Table of Contents
1. [Testing Overview](#testing-overview)
2. [Test Environment Setup](#test-environment-setup)
3. [Unit Testing](#unit-testing)
4. [Integration Testing](#integration-testing)
5. [End-to-End Testing](#end-to-end-testing)
6. [Performance Testing](#performance-testing)
7. [Security Testing](#security-testing)
8. [Test Data Management](#test-data-management)

## 🧪 Testing Overview

### Testing Strategy
The Smart Logistics System employs a comprehensive testing strategy that includes:
- **Unit Tests**: Individual component and function testing
- **Integration Tests**: API and service integration testing
- **End-to-End Tests**: Complete user workflow testing
- **Performance Tests**: Load and stress testing
- **Security Tests**: Vulnerability and penetration testing

### Testing Pyramid
```
    /\
   /  \     E2E Tests (10%)
  /____\    
 /      \   Integration Tests (20%)
/________\  Unit Tests (70%)
```

### Test Coverage Goals
- **Unit Tests**: >90% code coverage
- **Integration Tests**: All API endpoints covered
- **E2E Tests**: Critical user journeys covered
- **Performance Tests**: All major features tested under load

## 🔧 Test Environment Setup

### Prerequisites
```bash
# Node.js testing dependencies
npm install --save-dev jest @testing-library/react @testing-library/jest-dom
npm install --save-dev cypress @cypress/react

# Python testing dependencies
pip install pytest pytest-cov pytest-mock requests-mock
pip install selenium webdriver-manager
```

### Environment Configuration
Create test environment files:

#### Frontend Test Config
```javascript
// jest.config.js
module.exports = {
  testEnvironment: 'jsdom',
  setupFilesAfterEnv: ['<rootDir>/src/setupTests.js'],
  moduleNameMapping: {
    '\\.(css|less|scss|sass)$': 'identity-obj-proxy',
  },
  collectCoverageFrom: [
    'src/**/*.{js,jsx,ts,tsx}',
    '!src/index.js',
    '!src/reportWebVitals.js',
  ],
  coverageThreshold: {
    global: {
      branches: 80,
      functions: 80,
      lines: 80,
      statements: 80,
    },
  },
};
```

#### Backend Test Config
```python
# pytest.ini
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = --cov=backend --cov-report=html --cov-report=term-missing
markers =
    unit: Unit tests
    integration: Integration tests
    slow: Slow running tests
```

### Test Database Setup
```python
# conftest.py
import pytest
import tempfile
import os
from backend.app import create_app, init_db

@pytest.fixture
def app():
    db_fd, db_path = tempfile.mkstemp()
    app = create_app({
        'TESTING': True,
        'DATABASE': db_path,
    })
    
    with app.app_context():
        init_db()
    
    yield app
    
    os.close(db_fd)
    os.unlink(db_path)

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def runner(app):
    return app.test_cli_runner()
```

## 🔬 Unit Testing

### Frontend Unit Tests

#### Component Testing
```javascript
// src/components/__tests__/MetricCard.test.tsx
import React from 'react';
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import MetricCard from '../MetricCard';
import { Package } from 'lucide-react';

describe('MetricCard Component', () => {
  const defaultProps = {
    title: 'Total Deliveries',
    value: '1,247',
    change: '+12.5% from last month',
    changeType: 'positive' as const,
    icon: Package,
    color: 'blue' as const,
  };

  test('renders metric card with correct data', () => {
    render(<MetricCard {...defaultProps} />);
    
    expect(screen.getByText('Total Deliveries')).toBeInTheDocument();
    expect(screen.getByText('1,247')).toBeInTheDocument();
    expect(screen.getByText('+12.5% from last month')).toBeInTheDocument();
  });

  test('applies correct color classes', () => {
    const { container } = render(<MetricCard {...defaultProps} />);
    
    expect(container.firstChild).toHaveClass('bg-blue-50', 'border-blue-200');
  });

  test('handles different change types', () => {
    const negativeProps = { ...defaultProps, changeType: 'negative' as const };
    render(<MetricCard {...negativeProps} />);
    
    const changeElement = screen.getByText('+12.5% from last month');
    expect(changeElement).toHaveClass('text-red-600');
  });
});
```

#### Hook Testing
```javascript
// src/hooks/__tests__/useAuth.test.tsx
import { renderHook, act } from '@testing-library/react';
import { AuthProvider, useAuth } from '../contexts/AuthContext';

const wrapper = ({ children }) => <AuthProvider>{children}</AuthProvider>;

describe('useAuth Hook', () => {
  test('initial state is not authenticated', () => {
    const { result } = renderHook(() => useAuth(), { wrapper });
    
    expect(result.current.isAuthenticated).toBe(false);
    expect(result.current.user).toBe(null);
  });

  test('login updates authentication state', async () => {
    const { result } = renderHook(() => useAuth(), { wrapper });
    
    await act(async () => {
      const success = await result.current.login(
        'demo@smartlogistics.com',
        'demo123'
      );
      expect(success).toBe(true);
    });
    
    expect(result.current.isAuthenticated).toBe(true);
    expect(result.current.user).toEqual({
      username: 'demo@smartlogistics.com'
    });
  });

  test('logout clears authentication state', () => {
    const { result } = renderHook(() => useAuth(), { wrapper });
    
    act(() => {
      result.current.logout();
    });
    
    expect(result.current.isAuthenticated).toBe(false);
    expect(result.current.user).toBe(null);
  });
});
```

### Backend Unit Tests

#### API Endpoint Testing
```python
# tests/test_api.py
import pytest
import json
from backend.app import app

class TestAuthAPI:
    def test_login_success(self, client):
        response = client.post('/api/auth/login', 
            data=json.dumps({
                'email': 'demo@smartlogistics.com',
                'password': 'demo123'
            }),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'token' in data['data']

    def test_login_invalid_credentials(self, client):
        response = client.post('/api/auth/login',
            data=json.dumps({
                'email': 'invalid@email.com',
                'password': 'wrongpassword'
            }),
            content_type='application/json'
        )
        
        assert response.status_code == 401
        data = json.loads(response.data)
        assert data['success'] is False

class TestDataAPI:
    def test_upload_valid_csv(self, client):
        data = {
            'file': (io.BytesIO(b'order_id,date,quantity\n1,2024-01-01,5'), 'test.csv')
        }
        
        response = client.post('/api/upload-data', data=data)
        
        assert response.status_code == 200
        result = json.loads(response.data)
        assert result['success'] is True
        assert result['data']['records_processed'] > 0

    def test_upload_invalid_format(self, client):
        data = {
            'file': (io.BytesIO(b'invalid data'), 'test.txt')
        }
        
        response = client.post('/api/upload-data', data=data)
        
        assert response.status_code == 400
```

#### Machine Learning Model Testing
```python
# tests/test_lstm_forecasting.py
import pytest
import numpy as np
import pandas as pd
from backend.lstm_forecasting import AdvancedLSTMForecaster

class TestLSTMForecaster:
    @pytest.fixture
    def sample_data(self):
        dates = pd.date_range(start='2024-01-01', periods=100, freq='D')
        demand = np.random.normal(1000, 200, 100)
        return pd.DataFrame({'date': dates, 'demand': demand})

    @pytest.fixture
    def forecaster(self):
        return AdvancedLSTMForecaster(
            sequence_length=30,
            prediction_horizon=7
        )

    def test_data_preprocessing(self, forecaster, sample_data):
        X, y = forecaster.preprocess_data(sample_data)
        
        assert X.shape[0] > 0
        assert y.shape[0] > 0
        assert X.shape[0] == y.shape[0]

    def test_model_training(self, forecaster, sample_data):
        result = forecaster.train(sample_data)
        
        assert result['success'] is True
        assert 'epochs_trained' in result
        assert forecaster.is_trained is True

    def test_prediction_generation(self, forecaster, sample_data):
        # Train model first
        forecaster.train(sample_data)
        
        predictions = forecaster.predict(sample_data)
        
        assert 'predictions' in predictions
        assert len(predictions['predictions']) == 7
        assert all('predicted_demand' in pred for pred in predictions['predictions'])
```

#### Route Optimization Testing
```python
# tests/test_genetic_algorithm.py
import pytest
import numpy as np
from backend.genetic_algorithm import GeneticAlgorithmTSP

class TestGeneticAlgorithm:
    @pytest.fixture
    def sample_coordinates(self):
        return [
            (40.7829, -73.9654),  # Central Park
            (40.7580, -73.9855),  # Times Square
            (40.7061, -73.9969),  # Brooklyn Bridge
            (40.7484, -73.9857),  # Empire State Building
            (40.7074, -74.0113),  # Wall Street
        ]

    @pytest.fixture
    def ga_optimizer(self):
        return GeneticAlgorithmTSP(
            population_size=20,
            generations=10,
            mutation_rate=0.01
        )

    def test_distance_calculation(self, ga_optimizer):
        point1 = (40.7829, -73.9654)
        point2 = (40.7580, -73.9855)
        
        distance = ga_optimizer.calculate_distance(point1, point2)
        
        assert distance > 0
        assert isinstance(distance, float)

    def test_route_optimization(self, ga_optimizer, sample_coordinates):
        result = ga_optimizer.optimize(sample_coordinates)
        
        assert result['success'] is True
        assert 'best_route' in result
        assert 'best_distance' in result
        assert len(result['best_route']) == len(sample_coordinates)

    def test_fitness_calculation(self, ga_optimizer, sample_coordinates):
        route = [0, 1, 2, 3, 4]
        fitness = ga_optimizer.route_fitness(route, sample_coordinates)
        
        assert fitness > 0
        assert isinstance(fitness, float)
```

## 🔗 Integration Testing

### API Integration Tests
```python
# tests/test_integration.py
import pytest
import json
import tempfile
import os
from backend.app import app

class TestIntegrationWorkflow:
    def test_complete_forecasting_workflow(self, client):
        # 1. Upload data
        csv_data = "order_date,quantity\n2024-01-01,100\n2024-01-02,120"
        data = {
            'file': (io.BytesIO(csv_data.encode()), 'orders.csv')
        }
        
        upload_response = client.post('/api/upload-data', data=data)
        assert upload_response.status_code == 200
        
        # 2. Train model
        train_data = {
            'start_date': '2024-01-01',
            'end_date': '2024-01-31'
        }
        
        train_response = client.post('/api/train-forecast-model',
            data=json.dumps(train_data),
            content_type='application/json'
        )
        assert train_response.status_code == 200
        
        # 3. Generate predictions
        predict_data = {'days_ahead': 5}
        
        predict_response = client.post('/api/predict-demand',
            data=json.dumps(predict_data),
            content_type='application/json'
        )
        assert predict_response.status_code == 200
        
        result = json.loads(predict_response.data)
        assert 'predictions' in result
        assert len(result['predictions']) == 5

    def test_route_optimization_workflow(self, client):
        # 1. Submit delivery points
        route_data = {
            'delivery_points': [
                {
                    'id': 1,
                    'coordinates': [40.7829, -73.9654],
                    'address': 'Central Park, NYC'
                },
                {
                    'id': 2,
                    'coordinates': [40.7580, -73.9855],
                    'address': 'Times Square, NYC'
                }
            ],
            'algorithm': 'genetic'
        }
        
        response = client.post('/api/optimize-routes',
            data=json.dumps(route_data),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        result = json.loads(response.data)
        assert 'optimized_route' in result
        assert 'total_distance' in result
```

### Database Integration Tests
```python
# tests/test_database.py
import pytest
from backend.app import get_db_connection

class TestDatabaseOperations:
    def test_orders_crud_operations(self, app):
        with app.app_context():
            conn = get_db_connection()
            
            # Create
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO orders (order_date, customer_id, quantity, latitude, longitude)
                VALUES ('2024-01-01', 123, 5, 40.7128, -74.0060)
            """)
            order_id = cursor.lastrowid
            conn.commit()
            
            # Read
            cursor.execute("SELECT * FROM orders WHERE id = ?", (order_id,))
            order = cursor.fetchone()
            assert order is not None
            assert order['quantity'] == 5
            
            # Update
            cursor.execute("""
                UPDATE orders SET quantity = ? WHERE id = ?
            """, (10, order_id))
            conn.commit()
            
            cursor.execute("SELECT quantity FROM orders WHERE id = ?", (order_id,))
            updated_order = cursor.fetchone()
            assert updated_order['quantity'] == 10
            
            # Delete
            cursor.execute("DELETE FROM orders WHERE id = ?", (order_id,))
            conn.commit()
            
            cursor.execute("SELECT * FROM orders WHERE id = ?", (order_id,))
            deleted_order = cursor.fetchone()
            assert deleted_order is None
            
            conn.close()
```

## 🎭 End-to-End Testing

### Cypress E2E Tests
```javascript
// cypress/e2e/user_workflows.cy.js
describe('Smart Logistics System E2E Tests', () => {
  beforeEach(() => {
    cy.visit('/');
  });

  describe('Authentication Flow', () => {
    it('should login successfully with valid credentials', () => {
      cy.get('[data-testid=email-input]').type('demo@smartlogistics.com');
      cy.get('[data-testid=password-input]').type('demo123');
      cy.get('[data-testid=login-button]').click();
      
      cy.url().should('include', '/dashboard');
      cy.get('[data-testid=user-menu]').should('be.visible');
    });

    it('should show error with invalid credentials', () => {
      cy.get('[data-testid=email-input]').type('invalid@email.com');
      cy.get('[data-testid=password-input]').type('wrongpassword');
      cy.get('[data-testid=login-button]').click();
      
      cy.get('[data-testid=error-message]').should('be.visible');
      cy.get('[data-testid=error-message]').should('contain', 'Invalid credentials');
    });
  });

  describe('Dashboard Functionality', () => {
    beforeEach(() => {
      cy.login('demo@smartlogistics.com', 'demo123');
    });

    it('should display key metrics on dashboard', () => {
      cy.visit('/dashboard');
      
      cy.get('[data-testid=total-deliveries]').should('be.visible');
      cy.get('[data-testid=cost-savings]').should('be.visible');
      cy.get('[data-testid=delivery-time]').should('be.visible');
      cy.get('[data-testid=route-efficiency]').should('be.visible');
    });

    it('should navigate to different modules', () => {
      cy.get('[data-testid=nav-demand-forecasting]').click();
      cy.url().should('include', '/demand-forecasting');
      
      cy.get('[data-testid=nav-route-optimization]').click();
      cy.url().should('include', '/route-optimization');
      
      cy.get('[data-testid=nav-analytics]').click();
      cy.url().should('include', '/analytics');
    });
  });

  describe('Data Upload Workflow', () => {
    beforeEach(() => {
      cy.login('demo@smartlogistics.com', 'demo123');
      cy.visit('/data-management');
    });

    it('should upload CSV file successfully', () => {
      const fileName = 'sample_orders.csv';
      
      cy.get('[data-testid=file-upload]').selectFile({
        contents: Cypress.Buffer.from('order_id,date,quantity\n1,2024-01-01,5'),
        fileName: fileName,
        mimeType: 'text/csv',
      });
      
      cy.get('[data-testid=upload-button]').click();
      
      cy.get('[data-testid=upload-success]').should('be.visible');
      cy.get('[data-testid=file-list]').should('contain', fileName);
    });
  });

  describe('Route Optimization Workflow', () => {
    beforeEach(() => {
      cy.login('demo@smartlogistics.com', 'demo123');
      cy.visit('/route-optimization');
    });

    it('should add delivery points and optimize route', () => {
      // Add delivery point
      cy.get('[data-testid=address-input]').type('123 Main St, NYC');
      cy.get('[data-testid=add-point-button]').click();
      
      cy.get('[data-testid=delivery-points-list]').should('contain', '123 Main St, NYC');
      
      // Optimize route
      cy.get('[data-testid=optimize-button]').click();
      
      cy.get('[data-testid=optimization-results]', { timeout: 30000 }).should('be.visible');
      cy.get('[data-testid=route-metrics]').should('be.visible');
    });
  });
});
```

### Custom Cypress Commands
```javascript
// cypress/support/commands.js
Cypress.Commands.add('login', (email, password) => {
  cy.session([email, password], () => {
    cy.visit('/login');
    cy.get('[data-testid=email-input]').type(email);
    cy.get('[data-testid=password-input]').type(password);
    cy.get('[data-testid=login-button]').click();
    cy.url().should('include', '/dashboard');
  });
});

Cypress.Commands.add('uploadFile', (fileName, fileContent) => {
  cy.get('[data-testid=file-upload]').selectFile({
    contents: Cypress.Buffer.from(fileContent),
    fileName: fileName,
    mimeType: 'text/csv',
  });
  cy.get('[data-testid=upload-button]').click();
});
```

## ⚡ Performance Testing

### Load Testing with Artillery
```yaml
# artillery-config.yml
config:
  target: 'http://localhost:5000'
  phases:
    - duration: 60
      arrivalRate: 10
    - duration: 120
      arrivalRate: 20
    - duration: 60
      arrivalRate: 5
  defaults:
    headers:
      Content-Type: 'application/json'

scenarios:
  - name: "API Load Test"
    weight: 100
    flow:
      - post:
          url: "/api/auth/login"
          json:
            email: "demo@smartlogistics.com"
            password: "demo123"
          capture:
            - json: "$.data.token"
              as: "authToken"
      
      - get:
          url: "/api/performance-metrics"
          headers:
            Authorization: "Bearer {{ authToken }}"
      
      - post:
          url: "/api/optimize-routes"
          headers:
            Authorization: "Bearer {{ authToken }}"
          json:
            delivery_points:
              - id: 1
                coordinates: [40.7829, -73.9654]
                address: "Central Park, NYC"
              - id: 2
                coordinates: [40.7580, -73.9855]
                address: "Times Square, NYC"
            algorithm: "genetic"
```

### Frontend Performance Testing
```javascript
// tests/performance/lighthouse.test.js
const lighthouse = require('lighthouse');
const chromeLauncher = require('chrome-launcher');

describe('Performance Tests', () => {
  let chrome;
  let options;

  beforeAll(async () => {
    chrome = await chromeLauncher.launch({ chromeFlags: ['--headless'] });
    options = {
      logLevel: 'info',
      output: 'json',
      onlyCategories: ['performance'],
      port: chrome.port,
    };
  });

  afterAll(async () => {
    await chrome.kill();
  });

  test('Dashboard page performance', async () => {
    const runnerResult = await lighthouse('http://localhost:3000/dashboard', options);
    const score = runnerResult.lhr.categories.performance.score * 100;
    
    expect(score).toBeGreaterThan(80); // Minimum 80% performance score
  });

  test('Route optimization page performance', async () => {
    const runnerResult = await lighthouse('http://localhost:3000/route-optimization', options);
    const score = runnerResult.lhr.categories.performance.score * 100;
    
    expect(score).toBeGreaterThan(75); // Minimum 75% for complex pages
  });
});
```

## 🔒 Security Testing

### Authentication Security Tests
```python
# tests/test_security.py
import pytest
import json
from backend.app import app

class TestSecurityFeatures:
    def test_sql_injection_protection(self, client):
        # Attempt SQL injection in login
        malicious_payload = {
            'email': "admin'; DROP TABLE users; --",
            'password': 'password'
        }
        
        response = client.post('/api/auth/login',
            data=json.dumps(malicious_payload),
            content_type='application/json'
        )
        
        # Should not cause server error, should return 401
        assert response.status_code == 401

    def test_xss_protection(self, client):
        # Attempt XSS in data upload
        xss_payload = "<script>alert('xss')</script>"
        
        data = {
            'file': (io.BytesIO(f'order_id,address\n1,{xss_payload}'.encode()), 'test.csv')
        }
        
        response = client.post('/api/upload-data', data=data)
        
        # Should sanitize input
        assert '<script>' not in response.get_data(as_text=True)

    def test_csrf_protection(self, client):
        # Test CSRF token requirement
        response = client.post('/api/upload-data',
            data={'file': 'test'},
            headers={'Origin': 'http://malicious-site.com'}
        )
        
        assert response.status_code in [403, 400]  # Should reject cross-origin requests

    def test_rate_limiting(self, client):
        # Test rate limiting on login endpoint
        for i in range(10):
            response = client.post('/api/auth/login',
                data=json.dumps({
                    'email': 'test@example.com',
                    'password': 'wrongpassword'
                }),
                content_type='application/json'
            )
        
        # Should be rate limited after multiple attempts
        assert response.status_code == 429
```

### Penetration Testing Checklist
```bash
# security_tests.sh
#!/bin/bash

echo "Running security tests..."

# Test for common vulnerabilities
echo "1. Testing for SQL injection..."
sqlmap -u "http://localhost:5000/api/auth/login" --data="email=test&password=test" --batch

echo "2. Testing for XSS vulnerabilities..."
# Use XSStrike or similar tool

echo "3. Testing for CSRF protection..."
# Custom CSRF tests

echo "4. Testing SSL/TLS configuration..."
sslscan localhost:443

echo "5. Testing for sensitive data exposure..."
# Check for exposed configuration files, debug info, etc.

echo "Security tests completed."
```

## 📊 Test Data Management

### Test Data Factory
```python
# tests/factories.py
import factory
from datetime import datetime, timedelta
import random

class OrderFactory(factory.Factory):
    class Meta:
        model = dict

    order_id = factory.Sequence(lambda n: f"ORD{n:06d}")
    order_date = factory.LazyFunction(
        lambda: (datetime.now() - timedelta(days=random.randint(1, 365))).strftime('%Y-%m-%d')
    )
    customer_id = factory.Sequence(lambda n: f"CUST{n:04d}")
    quantity = factory.LazyFunction(lambda: random.randint(1, 100))
    latitude = factory.LazyFunction(lambda: round(40.7 + random.uniform(-0.1, 0.1), 6))
    longitude = factory.LazyFunction(lambda: round(-74.0 + random.uniform(-0.1, 0.1), 6))

class DeliveryPointFactory(factory.Factory):
    class Meta:
        model = dict

    id = factory.Sequence(lambda n: n)
    address = factory.Faker('address')
    coordinates = factory.LazyFunction(
        lambda: [40.7 + random.uniform(-0.1, 0.1), -74.0 + random.uniform(-0.1, 0.1)]
    )
    priority = factory.LazyFunction(lambda: random.choice(['High', 'Medium', 'Low']))
```

### Test Data Cleanup
```python
# tests/conftest.py
import pytest
import os
import tempfile

@pytest.fixture(autouse=True)
def cleanup_test_files():
    """Automatically cleanup test files after each test"""
    test_files = []
    
    yield test_files
    
    # Cleanup
    for file_path in test_files:
        if os.path.exists(file_path):
            os.remove(file_path)

@pytest.fixture
def temp_csv_file():
    """Create temporary CSV file for testing"""
    fd, path = tempfile.mkstemp(suffix='.csv')
    with os.fdopen(fd, 'w') as f:
        f.write('order_id,date,quantity\n1,2024-01-01,5\n2,2024-01-02,3\n')
    
    yield path
    
    if os.path.exists(path):
        os.remove(path)
```

### Running Tests

#### Frontend Tests
```bash
# Run all tests
npm test

# Run tests with coverage
npm test -- --coverage

# Run specific test file
npm test -- MetricCard.test.tsx

# Run tests in watch mode
npm test -- --watch
```

#### Backend Tests
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=backend --cov-report=html

# Run specific test file
pytest tests/test_api.py

# Run tests with specific marker
pytest -m unit
pytest -m integration
```

#### E2E Tests
```bash
# Run Cypress tests headlessly
npx cypress run

# Open Cypress test runner
npx cypress open

# Run specific test file
npx cypress run --spec "cypress/e2e/user_workflows.cy.js"
```

#### Performance Tests
```bash
# Run Artillery load tests
artillery run artillery-config.yml

# Run Lighthouse performance tests
npm run test:performance
```

---

*This testing guide provides comprehensive coverage for ensuring the quality, reliability, and security of the Smart Logistics System. Regular execution of these tests helps maintain high code quality and user experience.*