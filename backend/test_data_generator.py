"""
Test Data Generator for Smart Logistics System
Generates realistic test data for orders, routes, and forecasts
"""

import sqlite3
import random
from datetime import datetime, timedelta
import json


# NYC area coordinates (realistic delivery locations)
NYC_LOCATIONS = [
    {"name": "Manhattan - Midtown", "lat": 40.7580, "lon": -73.9855, "zone": "A"},
    {"name": "Manhattan - Upper West", "lat": 40.7829, "lon": -73.9654, "zone": "A"},
    {"name": "Manhattan - Lower East", "lat": 40.7168, "lon": -73.9861, "zone": "A"},
    {"name": "Brooklyn - Williamsburg", "lat": 40.7081, "lon": -73.9571, "zone": "B"},
    {"name": "Brooklyn - Park Slope", "lat": 40.6710, "lon": -73.9778, "zone": "B"},
    {"name": "Brooklyn - DUMBO", "lat": 40.7033, "lon": -73.9888, "zone": "B"},
    {"name": "Queens - Astoria", "lat": 40.7614, "lon": -73.9246, "zone": "C"},
    {"name": "Queens - Flushing", "lat": 40.7673, "lon": -73.8331, "zone": "C"},
    {"name": "Queens - Long Island City", "lat": 40.7447, "lon": -73.9485, "zone": "C"},
    {"name": "Bronx - Fordham", "lat": 40.8621, "lon": -73.8951, "zone": "D"},
    {"name": "Bronx - Riverdale", "lat": 40.8978, "lon": -73.9128, "zone": "D"},
    {"name": "Staten Island - St. George", "lat": 40.6437, "lon": -74.0737, "zone": "E"},
    {"name": "Manhattan - Financial District", "lat": 40.7074, "lon": -74.0113, "zone": "A"},
    {"name": "Manhattan - Harlem", "lat": 40.8116, "lon": -73.9465, "zone": "A"},
    {"name": "Brooklyn - Sunset Park", "lat": 40.6447, "lon": -74.0156, "zone": "B"},
    {"name": "Queens - Jamaica", "lat": 40.7023, "lon": -73.7887, "zone": "C"},
    {"name": "Bronx - South Bronx", "lat": 40.8215, "lon": -73.9219, "zone": "D"},
    {"name": "Brooklyn - Crown Heights", "lat": 40.6693, "lon": -73.9422, "zone": "B"},
    {"name": "Manhattan - East Village", "lat": 40.7264, "lon": -73.9818, "zone": "A"},
    {"name": "Queens - Forest Hills", "lat": 40.7189, "lon": -73.8448, "zone": "C"},
]

# Product catalog
PRODUCTS = [
    "PROD-001", "PROD-002", "PROD-003", "PROD-004", "PROD-005",
    "PROD-006", "PROD-007", "PROD-008", "PROD-009", "PROD-010",
    "PROD-011", "PROD-012", "PROD-013", "PROD-014", "PROD-015",
]

# Customer pool
CUSTOMER_IDS = list(range(1001, 1501))  # 500 customers


def generate_orders(num_orders: int = 1000, days_back: int = 90):
    """Generate realistic order data"""
    orders = []
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days_back)

    for i in range(num_orders):
        # Generate random date with higher frequency on weekdays
        random_days = random.randint(0, days_back)
        order_date = start_date + timedelta(days=random_days)

        # Increase orders on weekdays
        weekday = order_date.weekday()
        if weekday >= 5:  # Weekend
            if random.random() > 0.4:  # 60% skip weekends
                continue

        # Random location
        location = random.choice(NYC_LOCATIONS)

        # Add some noise to coordinates for variety
        lat = location["lat"] + random.uniform(-0.01, 0.01)
        lon = location["lon"] + random.uniform(-0.01, 0.01)

        # Generate delivery time (business hours)
        delivery_hour = random.randint(9, 18)
        delivery_minute = random.choice([0, 15, 30, 45])
        delivery_time = order_date.replace(
            hour=delivery_hour,
            minute=delivery_minute,
            second=0
        ) + timedelta(days=1)  # Next day delivery

        order = {
            "order_date": order_date.strftime("%Y-%m-%d"),
            "customer_id": random.choice(CUSTOMER_IDS),
            "product_id": random.choice(PRODUCTS),
            "quantity": random.randint(1, 10),
            "delivery_address": location["name"],
            "latitude": round(lat, 6),
            "longitude": round(lon, 6),
            "delivery_time": delivery_time.strftime("%Y-%m-%d %H:%M:%S"),
            "zone": location["zone"]
        }
        orders.append(order)

    return orders


def generate_routes(num_routes: int = 100):
    """Generate optimized route data"""
    routes = []
    algorithms = ["genetic", "ortools", "hybrid"]

    for i in range(num_routes):
        # Random vehicle ID
        vehicle_id = random.randint(1, 20)

        # Generate route sequence (5-15 stops)
        num_stops = random.randint(5, 15)
        route_sequence = [random.randint(1, 1000) for _ in range(num_stops)]

        # Calculate realistic metrics
        total_distance = num_stops * random.uniform(3, 8)  # km per stop
        estimated_time = num_stops * random.uniform(15, 30)  # minutes per stop

        # Optimization date in the past week
        opt_date = datetime.now() - timedelta(days=random.randint(0, 7))

        route = {
            "vehicle_id": vehicle_id,
            "route_sequence": json.dumps(route_sequence),
            "total_distance": round(total_distance, 2),
            "estimated_time": round(estimated_time, 2),
            "optimization_date": opt_date.strftime("%Y-%m-%d %H:%M:%S"),
            "algorithm_used": random.choice(algorithms)
        }
        routes.append(route)

    return routes


def generate_forecasts(num_forecasts: int = 100):
    """Generate demand forecast data"""
    forecasts = []

    # Generate forecasts for next 30 days
    for product in PRODUCTS[:5]:  # Top 5 products
        for day in range(30):
            forecast_date = datetime.now() + timedelta(days=day)

            # Realistic demand with trends
            base_demand = random.randint(50, 150)
            weekday_factor = 1.2 if forecast_date.weekday() < 5 else 0.7
            trend = day * 0.5  # Slight upward trend

            predicted_demand = base_demand * weekday_factor + trend
            confidence_interval = predicted_demand * random.uniform(0.1, 0.2)

            forecast = {
                "product_id": product,
                "forecast_date": forecast_date.strftime("%Y-%m-%d"),
                "predicted_demand": round(predicted_demand, 2),
                "confidence_interval": round(confidence_interval, 2),
                "model_version": f"v{random.randint(1, 3)}.0",
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            forecasts.append(forecast)

    return forecasts


def insert_test_data(database_path: str = "smart_logistics.db"):
    """Insert all test data into database"""
    print("🚀 Generating test data...")

    # Generate data
    orders = generate_orders(num_orders=2000, days_back=90)
    routes = generate_routes(num_routes=200)
    forecasts = generate_forecasts()

    print(f"✅ Generated {len(orders)} orders")
    print(f"✅ Generated {len(routes)} routes")
    print(f"✅ Generated {len(forecasts)} forecasts")

    # Connect to database
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()

    # Clear existing data
    print("\n🗑️  Clearing existing data...")
    cursor.execute("DELETE FROM orders")
    cursor.execute("DELETE FROM optimized_routes")
    cursor.execute("DELETE FROM demand_forecasts")

    # Insert orders
    print("\n📦 Inserting orders...")
    for order in orders:
        cursor.execute('''
            INSERT INTO orders 
            (order_date, customer_id, product_id, quantity, delivery_address, 
             latitude, longitude, delivery_time, zone)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            order["order_date"],
            order["customer_id"],
            order["product_id"],
            order["quantity"],
            order["delivery_address"],
            order["latitude"],
            order["longitude"],
            order["delivery_time"],
            order["zone"]
        ))

    # Insert routes
    print("🚛 Inserting routes...")
    for route in routes:
        cursor.execute('''
            INSERT INTO optimized_routes 
            (vehicle_id, route_sequence, total_distance, estimated_time, 
             optimization_date, algorithm_used)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            route["vehicle_id"],
            route["route_sequence"],
            route["total_distance"],
            route["estimated_time"],
            route["optimization_date"],
            route["algorithm_used"]
        ))

    # Insert forecasts
    print("📈 Inserting forecasts...")
    for forecast in forecasts:
        cursor.execute('''
            INSERT INTO demand_forecasts 
            (product_id, forecast_date, predicted_demand, confidence_interval, 
             model_version, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            forecast["product_id"],
            forecast["forecast_date"],
            forecast["predicted_demand"],
            forecast["confidence_interval"],
            forecast["model_version"],
            forecast["created_at"]
        ))

    conn.commit()

    # Verify data
    cursor.execute("SELECT COUNT(*) FROM orders")
    order_count = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM optimized_routes")
    route_count = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM demand_forecasts")
    forecast_count = cursor.fetchone()[0]

    conn.close()

    print("\n✅ Test data insertion complete!")
    print(f"   Orders in DB: {order_count}")
    print(f"   Routes in DB: {route_count}")
    print(f"   Forecasts in DB: {forecast_count}")

    return {
        "orders": order_count,
        "routes": route_count,
        "forecasts": forecast_count
    }


if __name__ == "__main__":
    insert_test_data()

