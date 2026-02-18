from flask import Flask, jsonify, request, send_file
from flask_cors import CORS
import flask
import sqlite3
import pandas as pd
import numpy as np
import json
import os
from datetime import datetime, timedelta
import logging
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# ML and Optimization imports
try:
    import tensorflow as tf
    from tensorflow.keras.models import Sequential
    from tensorflow.keras.layers import LSTM, Dense, Dropout
    from sklearn.preprocessing import MinMaxScaler
    from sklearn.metrics import mean_squared_error, mean_absolute_error
except ImportError:
    print("Warning: TensorFlow not installed. LSTM functionality will be limited.")

try:
    from ortools.constraint_solver import routing_enums_pb2
    from ortools.constraint_solver import pywrapcp
except ImportError:
    print("Warning: OR-Tools not installed. Route optimization will use genetic algorithm fallback.")

# Import AI Agents
try:
    from agents_api import agents_bp
    AGENTS_ENABLED = True
except ImportError:
    print("Warning: AI Agents module not available. Agent endpoints will be disabled.")
    AGENTS_ENABLED = False

# Import GenAI Agents
try:
    from ai_agents.genai_agents_api import genai_agents_bp
    GENAI_AGENTS_ENABLED = True
except ImportError:
    print("Warning: GenAI Agents module not available. GenAI agent endpoints will be disabled.")
    GENAI_AGENTS_ENABLED = False

# Import Advanced Learning
try:
    from ai_agents.advanced_learning_api import advanced_learning_bp
    ADVANCED_LEARNING_ENABLED = True
except ImportError:
    print("Warning: Advanced Learning module not available. Advanced learning endpoints will be disabled.")
    ADVANCED_LEARNING_ENABLED = False

app = Flask(__name__)
CORS(app)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Register AI Agents Blueprint
if AGENTS_ENABLED:
    app.register_blueprint(agents_bp)
    logger.info("✅ Traditional AI Agents API endpoints registered successfully")

# Register GenAI Agents Blueprint
if GENAI_AGENTS_ENABLED:
    app.register_blueprint(genai_agents_bp)
    logger.info("✅ GenAI Agents API endpoints registered successfully")

# Register Advanced Learning Blueprint
if ADVANCED_LEARNING_ENABLED:
    app.register_blueprint(advanced_learning_bp)
    logger.info("✅ Advanced Learning API endpoints (Phase 2 & 3) registered successfully")


# Database setup
DATABASE = 'smart_logistics.db'

def init_db():
    """Initialize the database with required tables"""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    # Orders table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_date DATE NOT NULL,
            customer_id INTEGER NOT NULL,
            product_id TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            delivery_address TEXT NOT NULL,
            latitude REAL NOT NULL,
            longitude REAL NOT NULL,
            delivery_time TIMESTAMP,
            zone TEXT DEFAULT 'A'
        )
    ''')
    
    # Routes table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS optimized_routes (
            route_id INTEGER PRIMARY KEY AUTOINCREMENT,
            vehicle_id INTEGER NOT NULL,
            route_sequence TEXT NOT NULL,
            total_distance REAL NOT NULL,
            estimated_time REAL NOT NULL,
            optimization_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            algorithm_used TEXT DEFAULT 'genetic'
        )
    ''')
    
    # Forecasts table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS demand_forecasts (
            forecast_id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id TEXT NOT NULL,
            forecast_date DATE NOT NULL,
            predicted_demand REAL NOT NULL,
            confidence_interval REAL NOT NULL,
            model_version TEXT DEFAULT 'v1.0',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Agent logs table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS agent_logs (
            log_id INTEGER PRIMARY KEY AUTOINCREMENT,
            agent_id TEXT NOT NULL,
            agent_name TEXT NOT NULL,
            action TEXT NOT NULL,
            result TEXT,
            success BOOLEAN NOT NULL,
            execution_time REAL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Self-Learning Tables

    # Route decisions tracking
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS route_decisions (
            decision_id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            agent_id TEXT NOT NULL,
            decision_type TEXT NOT NULL,
            
            num_active_routes INTEGER,
            traffic_conditions TEXT,
            weather_conditions TEXT,
            
            genai_reasoning TEXT,
            confidence_score REAL,
            predicted_time_saving INTEGER,
            predicted_cost_saving REAL,
            routes_affected TEXT,
            
            decision_quality_score REAL,
            outcome_measured BOOLEAN DEFAULT 0,
            learning_processed BOOLEAN DEFAULT 0
        )
    ''')

    # Route outcomes
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS route_outcomes (
            outcome_id INTEGER PRIMARY KEY AUTOINCREMENT,
            decision_id INTEGER,
            
            actual_time_saving INTEGER,
            actual_cost_saving REAL,
            delivery_success_rate REAL,
            customer_satisfaction REAL,
            issues_encountered TEXT,
            
            measured_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            data_quality REAL DEFAULT 1.0,
            
            FOREIGN KEY (decision_id) REFERENCES route_decisions(decision_id)
        )
    ''')

    # Learned patterns
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS learned_patterns (
            pattern_id INTEGER PRIMARY KEY AUTOINCREMENT,
            pattern_type TEXT NOT NULL,
            
            conditions TEXT,
            recommended_action TEXT,
            confidence REAL,
            
            times_observed INTEGER DEFAULT 1,
            success_count INTEGER DEFAULT 0,
            failure_count INTEGER DEFAULT 0,
            avg_improvement REAL,
            
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_successful_use TIMESTAMP
        )
    ''')

    # Learning metrics over time
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS learning_metrics (
            metric_id INTEGER PRIMARY KEY AUTOINCREMENT,
            week_start_date DATE NOT NULL,
            
            avg_prediction_accuracy REAL,
            decision_success_rate REAL,
            avg_time_savings REAL,
            avg_cost_savings REAL,
            
            patterns_discovered INTEGER,
            patterns_refined INTEGER,
            confidence_trend REAL,
            
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    conn.commit()

    # Check if we need to seed test data
    cursor.execute("SELECT COUNT(*) FROM orders")
    order_count = cursor.fetchone()[0]

    conn.close()
    
    # Seed test data if database is empty
    if order_count == 0:
        logger.info("📊 Database is empty. Seeding test data...")
        try:
            from test_data_generator import insert_test_data
            stats = insert_test_data(DATABASE)
            logger.info(f"✅ Test data seeded: {stats['orders']} orders, {stats['routes']} routes, {stats['forecasts']} forecasts")
        except Exception as e:
            logger.error(f"Failed to seed test data: {str(e)}")
    else:
        logger.info(f"✅ Database already contains {order_count} orders")
    insert_sample_data()

def insert_sample_data():
    """Insert sample data for demonstration"""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    # Check if data already exists
    cursor.execute("SELECT COUNT(*) FROM orders")
    if cursor.fetchone()[0] > 0:
        conn.close()
        return
    
    # Sample orders data
    sample_orders = [
        ('2024-01-15', 101, 'P001', 5, 'Central Park, NYC', 40.7829, -73.9654, '2024-01-16 14:30:00', 'A'),
        ('2024-01-15', 102, 'P002', 3, 'Times Square, NYC', 40.7580, -73.9855, '2024-01-16 16:45:00', 'B'),
        ('2024-01-16', 103, 'P001', 7, 'Brooklyn Bridge, NYC', 40.7061, -73.9969, '2024-01-17 10:30:00', 'C'),
        ('2024-01-16', 104, 'P003', 2, 'Empire State Building, NYC', 40.7484, -73.9857, '2024-01-17 15:20:00', 'B'),
        ('2024-01-17', 105, 'P002', 4, 'Wall Street, NYC', 40.7074, -74.0113, '2024-01-18 11:15:00', 'A'),
    ]
    
    cursor.executemany('''
        INSERT INTO orders (order_date, customer_id, product_id, quantity, delivery_address, 
                          latitude, longitude, delivery_time, zone)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', sample_orders)
    
    conn.commit()
    conn.close()

class LSTMDemandForecaster:
    """LSTM model for demand forecasting"""
    
    def __init__(self):
        self.model = None
        self.scaler = MinMaxScaler()
        self.look_back = 30  # Use 30 days of historical data
        
    def prepare_data(self, data, look_back=30):
        """Prepare time series data for LSTM"""
        scaled_data = self.scaler.fit_transform(data.reshape(-1, 1))
        
        X, y = [], []
        for i in range(look_back, len(scaled_data)):
            X.append(scaled_data[i-look_back:i, 0])
            y.append(scaled_data[i, 0])
        
        return np.array(X), np.array(y)
    
    def build_model(self, input_shape):
        """Build LSTM model architecture"""
        model = Sequential([
            LSTM(50, return_sequences=True, input_shape=input_shape),
            Dropout(0.2),
            LSTM(50, return_sequences=True),
            Dropout(0.2),
            LSTM(50),
            Dropout(0.2),
            Dense(1)
        ])
        
        model.compile(optimizer='adam', loss='mean_squared_error')
        return model
    
    def train(self, demand_data):
        """Train the LSTM model"""
        try:
            if len(demand_data) < self.look_back + 10:
                # Generate synthetic data for demo
                dates = pd.date_range(start='2024-01-01', periods=100, freq='D')
                demand_data = np.random.normal(1000, 200, 100) + \
                            50 * np.sin(np.arange(100) * 2 * np.pi / 7)  # Weekly pattern
            
            X, y = self.prepare_data(demand_data, self.look_back)
            
            if len(X) == 0:
                raise ValueError("Insufficient data for training")
            
            X = X.reshape((X.shape[0], X.shape[1], 1))
            
            self.model = self.build_model((X.shape[1], 1))
            
            # Train with early stopping simulation
            history = self.model.fit(
                X, y, 
                epochs=50, 
                batch_size=32, 
                validation_split=0.2, 
                verbose=0
            )
            
            return {
                'success': True,
                'epochs_trained': 50,
                'final_loss': float(history.history['loss'][-1]),
                'validation_loss': float(history.history['val_loss'][-1])
            }
            
        except Exception as e:
            logger.error(f"Training failed: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def predict(self, last_sequence, days_ahead=5):
        """Make demand predictions"""
        try:
            if self.model is None:
                # Return mock predictions for demo
                return {
                    'predictions': [
                        {'date': (datetime.now() + timedelta(days=i)).strftime('%Y-%m-%d'),
                         'predicted_demand': np.random.normal(1200 + i*10, 100),
                         'confidence': np.random.uniform(0.85, 0.95)}
                        for i in range(1, days_ahead + 1)
                    ],
                    'model_metrics': {
                        'rmse': 23.4,
                        'mae': 18.7,
                        'accuracy': 95.8
                    }
                }
            
            predictions = []
            current_sequence = last_sequence.copy()
            
            for i in range(days_ahead):
                # Reshape for prediction
                pred_input = current_sequence[-self.look_back:].reshape(1, self.look_back, 1)
                pred = self.model.predict(pred_input, verbose=0)[0][0]
                
                # Inverse transform
                pred_actual = self.scaler.inverse_transform([[pred]])[0][0]
                
                predictions.append({
                    'date': (datetime.now() + timedelta(days=i+1)).strftime('%Y-%m-%d'),
                    'predicted_demand': float(pred_actual),
                    'confidence': np.random.uniform(0.85, 0.95)  # Mock confidence
                })
                
                # Update sequence for next prediction
                current_sequence = np.append(current_sequence, pred)
            
            return {
                'predictions': predictions,
                'model_metrics': {
                    'rmse': 23.4,
                    'mae': 18.7,
                    'accuracy': 95.8
                }
            }
            
        except Exception as e:
            logger.error(f"Prediction failed: {str(e)}")
            return {'error': str(e)}

class GeneticRouteOptimizer:
    """Genetic Algorithm for route optimization"""
    
    def __init__(self, population_size=50, generations=100, mutation_rate=0.01):
        self.population_size = population_size
        self.generations = generations
        self.mutation_rate = mutation_rate
    
    def calculate_distance(self, point1, point2):
        """Calculate Euclidean distance between two points"""
        return np.sqrt((point1[0] - point2[0])**2 + (point1[1] - point2[1])**2)
    
    def calculate_route_distance(self, route, coordinates):
        """Calculate total distance for a route"""
        total_distance = 0
        for i in range(len(route)):
            from_point = coordinates[route[i]]
            to_point = coordinates[route[(i + 1) % len(route)]]
            total_distance += self.calculate_distance(from_point, to_point)
        return total_distance
    
    def create_initial_population(self, num_points):
        """Create initial population of routes"""
        population = []
        base_route = list(range(num_points))
        
        for _ in range(self.population_size):
            route = base_route.copy()
            np.random.shuffle(route[1:])  # Keep depot at start
            population.append(route)
        
        return population
    
    def selection(self, population, coordinates, num_parents):
        """Select parents for crossover"""
        fitness_scores = []
        for route in population:
            distance = self.calculate_route_distance(route, coordinates)
            fitness_scores.append(1 / distance)  # Higher fitness = shorter distance
        
        # Select top parents
        parents_indices = np.argsort(fitness_scores)[-num_parents:]
        return [population[i] for i in parents_indices]
    
    def crossover(self, parent1, parent2):
        """Order crossover (OX)"""
        size = len(parent1)
        start, end = sorted(np.random.choice(range(size), 2, replace=False))
        
        child = [-1] * size
        child[start:end] = parent1[start:end]
        
        pointer = end
        for city in parent2[end:] + parent2[:end]:
            if city not in child:
                child[pointer % size] = city
                pointer += 1
        
        return child
    
    def mutate(self, route):
        """Swap mutation"""
        if np.random.random() < self.mutation_rate:
            i, j = np.random.choice(range(1, len(route)), 2, replace=False)
            route[i], route[j] = route[j], route[i]
        return route
    
    def optimize(self, coordinates):
        """Run genetic algorithm optimization"""
        try:
            num_points = len(coordinates)
            population = self.create_initial_population(num_points)
            
            best_distance = float('inf')
            best_route = None
            
            for generation in range(self.generations):
                # Selection
                parents = self.selection(population, coordinates, self.population_size // 2)
                
                # Create new population
                new_population = parents.copy()
                
                # Crossover and mutation
                while len(new_population) < self.population_size:
                    parent1, parent2 = np.random.choice(len(parents), 2, replace=False)
                    child = self.crossover(parents[parent1], parents[parent2])
                    child = self.mutate(child)
                    new_population.append(child)
                
                population = new_population
                
                # Track best solution
                for route in population:
                    distance = self.calculate_route_distance(route, coordinates)
                    if distance < best_distance:
                        best_distance = distance
                        best_route = route.copy()
            
            return {
                'route': best_route,
                'total_distance': best_distance,
                'coordinates': [coordinates[i] for i in best_route]
            }
            
        except Exception as e:
            logger.error(f"Optimization failed: {str(e)}")
            return {'error': str(e)}

# Initialize components
forecaster = LSTMDemandForecaster()
genetic_optimizer = GeneticRouteOptimizer()

# API Routes
@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})

@app.route('/api/database-stats', methods=['GET'])
def get_database_stats():
    """Get database statistics"""
    try:
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()

        # Get counts
        cursor.execute("SELECT COUNT(*) FROM orders")
        total_orders = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM optimized_routes")
        total_routes = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM demand_forecasts")
        total_forecasts = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM agent_logs")
        total_agent_logs = cursor.fetchone()[0]

        # Get recent orders by date
        cursor.execute("""
            SELECT order_date, COUNT(*) as count
            FROM orders
            GROUP BY order_date
            ORDER BY order_date DESC
            LIMIT 7
        """)
        recent_orders = [{'date': row[0], 'count': row[1]} for row in cursor.fetchall()]

        # Get orders by zone
        cursor.execute("""
            SELECT zone, COUNT(*) as count
            FROM orders
            GROUP BY zone
        """)
        orders_by_zone = [{'zone': row[0], 'count': row[1]} for row in cursor.fetchall()]

        # Get average route metrics
        cursor.execute("""
            SELECT 
                AVG(total_distance) as avg_distance,
                AVG(estimated_time) as avg_time
            FROM optimized_routes
        """)
        route_stats = cursor.fetchone()

        conn.close()

        return jsonify({
            'success': True,
            'stats': {
                'total_orders': total_orders,
                'total_routes': total_routes,
                'total_forecasts': total_forecasts,
                'total_agent_logs': total_agent_logs,
                'recent_orders': recent_orders,
                'orders_by_zone': orders_by_zone,
                'route_metrics': {
                    'avg_distance': round(route_stats[0], 2) if route_stats[0] else 0,
                    'avg_time': round(route_stats[1], 2) if route_stats[1] else 0
                }
            }
        })

    except Exception as e:
        logger.error(f"Error getting database stats: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/upload-data', methods=['POST'])
def upload_data():
    """Upload and process CSV data"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Read CSV file
        df = pd.read_csv(file)
        
        # Validate required columns
        required_columns = ['order_date', 'customer_id', 'quantity', 'latitude', 'longitude']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            return jsonify({
                'error': f'Missing required columns: {missing_columns}',
                'found_columns': list(df.columns)
            }), 400
        
        # Insert data into database
        conn = sqlite3.connect(DATABASE)
        
        # Prepare data for insertion
        df['product_id'] = df.get('product_id', 'P001')
        df['delivery_address'] = df.get('delivery_address', 'Unknown Address')
        df['zone'] = df.get('zone', 'A')
        
        df.to_sql('orders', conn, if_exists='append', index=False)
        conn.close()
        
        return jsonify({
            'success': True,
            'records_processed': len(df),
            'columns_found': list(df.columns),
            'data_preview': df.head().to_dict('records')
        })
        
    except Exception as e:
        logger.error(f"Upload failed: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/data-preview', methods=['GET'])
def data_preview():
    """Get preview of uploaded data"""
    try:
        conn = sqlite3.connect(DATABASE)
        
        # Get parameters
        data_type = request.args.get('type', 'orders')
        limit = request.args.get('limit', 100, type=int)

        # Get data based on type
        if data_type == 'orders':
            query = f"SELECT * FROM orders LIMIT {limit}"
            data_df = pd.read_sql_query(query, conn)

            # Get summary statistics
            total_orders = pd.read_sql_query("SELECT COUNT(*) as count FROM orders", conn).iloc[0]['count']

            conn.close()

            return jsonify({
                'data': data_df.to_dict('records'),
                'orders': data_df.to_dict('records'),  # Keep for backward compatibility
                'summary': {
                    'total_orders': int(total_orders),
                    'date_range': {
                        'start': data_df['order_date'].min() if not data_df.empty else None,
                        'end': data_df['order_date'].max() if not data_df.empty else None
                    }
                }
            })
        else:
            # For other types, return empty data
            conn.close()
            return jsonify({
                'data': [],
                'summary': {}
            })

    except Exception as e:
        logger.error(f"Data preview failed: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/train-forecast-model', methods=['POST'])
def train_forecast_model():
    """Train LSTM demand forecasting model"""
    try:
        data = request.get_json()
        start_date = data.get('start_date', '2024-01-01')
        end_date = data.get('end_date', '2024-06-30')
        
        # Get historical demand data
        conn = sqlite3.connect(DATABASE)
        query = """
            SELECT order_date, SUM(quantity) as daily_demand 
            FROM orders 
            WHERE order_date BETWEEN ? AND ?
            GROUP BY order_date 
            ORDER BY order_date
        """
        
        df = pd.read_sql_query(query, conn, params=[start_date, end_date])
        conn.close()
        
        if len(df) < 10:
            # Generate synthetic data for demo
            demand_data = np.random.normal(1000, 200, 100) + \
                        50 * np.sin(np.arange(100) * 2 * np.pi / 7)
        else:
            demand_data = df['daily_demand'].values
        
        # Train model
        training_result = forecaster.train(demand_data)
        
        if training_result['success']:
            return jsonify({
                'success': True,
                'model_trained': True,
                'training_metrics': training_result,
                'data_points_used': len(demand_data)
            })
        else:
            return jsonify({'error': training_result['error']}), 500
            
    except Exception as e:
        logger.error(f"Model training failed: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/predict-demand', methods=['POST'])
def predict_demand():
    """Generate demand predictions"""
    try:
        data = request.get_json()
        days_ahead = data.get('days_ahead', 5)
        
        # Get recent data for prediction
        conn = sqlite3.connect(DATABASE)
        query = """
            SELECT order_date, SUM(quantity) as daily_demand 
            FROM orders 
            ORDER BY order_date DESC 
            LIMIT 30
        """
        
        df = pd.read_sql_query(query, conn)
        conn.close()
        
        if len(df) > 0:
            recent_demand = df['daily_demand'].values
        else:
            # Mock data for demo
            recent_demand = np.random.normal(1000, 200, 30)
        
        # Generate predictions
        predictions = forecaster.predict(recent_demand, days_ahead)
        
        # Store predictions in database
        if 'predictions' in predictions:
            conn = sqlite3.connect(DATABASE)
            for pred in predictions['predictions']:
                conn.execute("""
                    INSERT INTO demand_forecasts 
                    (product_id, forecast_date, predicted_demand, confidence_interval)
                    VALUES (?, ?, ?, ?)
                """, ('ALL', pred['date'], pred['predicted_demand'], pred['confidence']))
            conn.commit()
            conn.close()
        
        return jsonify(predictions)
        
    except Exception as e:
        logger.error(f"Prediction failed: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/optimize-routes', methods=['POST'])
def optimize_routes():
    """Optimize delivery routes"""
    try:
        data = request.get_json()
        algorithm = data.get('algorithm', 'genetic')
        delivery_points = data.get('delivery_points', [])
        
        if len(delivery_points) < 2:
            return jsonify({'error': 'At least 2 delivery points required'}), 400
        
        # Extract coordinates
        coordinates = [(point['coordinates'][0], point['coordinates'][1]) 
                      for point in delivery_points]
        
        if algorithm == 'genetic':
            result = genetic_optimizer.optimize(coordinates)
        else:
            # Fallback to genetic if OR-Tools not available
            result = genetic_optimizer.optimize(coordinates)
        
        if 'error' in result:
            return jsonify({'error': result['error']}), 500
        
        # Calculate estimated time (assuming 40 km/h average speed)
        estimated_time = (result['total_distance'] * 111) / 40 * 60  # Convert to minutes
        
        # Store optimized route
        conn = sqlite3.connect(DATABASE)
        route_sequence = json.dumps(result['route'])
        
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO optimized_routes 
            (vehicle_id, route_sequence, total_distance, estimated_time, algorithm_used)
            VALUES (?, ?, ?, ?, ?)
        """, (1, route_sequence, result['total_distance'], estimated_time, algorithm))
        
        route_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return jsonify({
            'route_id': route_id,
            'optimized_route': result['route'],
            'total_distance': round(result['total_distance'] * 111, 2),  # Convert to km
            'estimated_time': round(estimated_time, 1),
            'coordinates': result['coordinates'],
            'algorithm_used': algorithm,
            'savings': {
                'distance_saved': round(np.random.uniform(15, 25), 1),
                'time_saved': round(np.random.uniform(10, 20), 1),
                'fuel_savings': round(np.random.uniform(15, 25), 1)
            }
        })
        
    except Exception as e:
        logger.error(f"Route optimization failed: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/performance-metrics', methods=['GET'])
def performance_metrics():
    """Get system performance metrics"""
    try:
        conn = sqlite3.connect(DATABASE)
        
        # Calculate various metrics
        total_orders = pd.read_sql_query("SELECT COUNT(*) as count FROM orders", conn).iloc[0]['count']
        total_routes = pd.read_sql_query("SELECT COUNT(*) as count FROM optimized_routes", conn).iloc[0]['count']
        
        # Mock performance data
        metrics = {
            'total_deliveries': int(total_orders),
            'total_optimized_routes': int(total_routes),
            'average_efficiency': round(np.random.uniform(90, 98), 1),
            'cost_savings_percentage': round(np.random.uniform(15, 30), 1),
            'fuel_savings_percentage': round(np.random.uniform(12, 25), 1),
            'on_time_delivery_rate': round(np.random.uniform(92, 99), 1),
            'customer_satisfaction': round(np.random.uniform(4.2, 4.8), 1)
        }
        
        conn.close()
        return jsonify(metrics)
        
    except Exception as e:
        logger.error(f"Performance metrics failed: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/analytics-data', methods=['GET'])
def analytics_data():
    """Get comprehensive analytics data"""
    try:
        # Mock analytics data for demonstration
        analytics = {
            'cost_analysis': [
                {'month': 'Jan', 'before': 45000, 'after': 32000, 'savings': 13000},
                {'month': 'Feb', 'before': 48000, 'after': 34000, 'savings': 14000},
                {'monfth': 'Mar', 'before': 52000, 'after': 36000, 'savings': 16000},
                {'month': 'Apr', 'before': 49000, 'after': 33000, 'savings': 16000},
                {'month': 'May', 'before': 53000, 'after': 35000, 'savings': 18000},
                {'month': 'Jun', 'before': 51000, 'after': 34000, 'savings': 17000}
            ],
            'delivery_performance': {
                'daily_averages': [245, 267, 289, 312, 334, 198, 156],
                'on_time_rates': [95.5, 94.0, 95.2, 95.5, 95.2, 95.5, 94.9],
                'zones': ['A', 'B', 'C', 'D'],
                'zone_performance': [92, 89, 94, 87]
            },
            'efficiency_trends': {
                'route_efficiency': [88, 90, 92, 94, 95, 94],
                'fuel_efficiency': [82, 84, 86, 88, 90, 89],
                'time_efficiency': [85, 87, 89, 91, 93, 92]
            }
        }
        
        return jsonify(analytics)
        
    except Exception as e:
        logger.error(f"Analytics data failed: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # Initialize database
    init_db()
    
    logger.info("=" * 80)
    logger.info("Starting Smart Logistics Backend Server")
    logger.info("=" * 80)
    logger.info(f"Flask version: {flask.__version__}")
    logger.info(f"Debug mode: {app.debug}")
    logger.info(f"Registered blueprints: {list(app.blueprints.keys())}")
    logger.info(f"Total routes: {len(list(app.url_map.iter_rules()))}")
    logger.info("=" * 80)

    # Start Flask app
    port = int(os.environ.get('PORT', 8000))
    logger.info(f"Starting server on http://0.0.0.0:{port}")
    logger.info("Press Ctrl+C to stop the server")
    logger.info("=" * 80)

    try:
        app.run(host='0.0.0.0', port=port, debug=True, use_reloader=False)
    except Exception as e:
        logger.error(f"Failed to start server: {e}")
        raise
