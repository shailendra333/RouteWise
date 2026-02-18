"""
Quick script to populate the database with sample order data
Run this if you get "No orders data available" error when executing agents
"""
import sqlite3
import random
from datetime import datetime, timedelta

DATABASE = 'smart_logistics.db'

def generate_sample_orders(num_orders=100):
    """Generate sample order data"""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    print(f"Generating {num_orders} sample orders...")
    
    # Sample data
    zones = ['A', 'B', 'C', 'D']
    products = ['P001', 'P002', 'P003', 'P004', 'P005']
    
    # NYC coordinates range
    lat_range = (40.7000, 40.8000)
    lon_range = (-74.0200, -73.9000)
    
    start_date = datetime.now() - timedelta(days=90)
    
    orders = []
    for i in range(num_orders):
        order_date = start_date + timedelta(days=random.randint(0, 90))
        customer_id = random.randint(1000, 9999)
        product_id = random.choice(products)
        quantity = random.randint(1, 20)
        latitude = random.uniform(*lat_range)
        longitude = random.uniform(*lon_range)
        zone = random.choice(zones)
        delivery_address = f"Address {i+1}, NYC"
        
        orders.append((
            order_date.strftime('%Y-%m-%d'),
            customer_id,
            product_id,
            quantity,
            delivery_address,
            latitude,
            longitude,
            zone
        ))
    
    # Insert orders
    cursor.executemany('''
        INSERT INTO orders (order_date, customer_id, product_id, quantity, delivery_address, latitude, longitude, zone)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', orders)
    
    conn.commit()
    
    # Verify
    count = cursor.execute("SELECT COUNT(*) FROM orders").fetchone()[0]
    print(f"✅ Successfully added {num_orders} orders!")
    print(f"Total orders in database: {count}")
    
    # Show sample
    print("\nSample orders:")
    samples = cursor.execute("SELECT * FROM orders LIMIT 5").fetchall()
    for order in samples:
        print(f"  Order ID: {order[0]}, Date: {order[1]}, Quantity: {order[4]}, Zone: {order[8]}")
    
    conn.close()

if __name__ == '__main__':
    try:
        generate_sample_orders(100)
        print("\n✅ Database populated successfully!")
        print("You can now run the agents from the UI.")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

