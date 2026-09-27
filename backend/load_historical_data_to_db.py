"""
Load Generated Historical Data into smart_logistics.db

generate_historical_data.py produces realistic 5-year seasonal/growth/holiday
patterns, but those CSVs were never wired into the live app: /api/train-forecast-model
and /api/predict-demand read from the `orders` table, and the AI demand-predictor
agent reads `historical_orders` from the same table. With only a handful of sample
orders seeded, both features silently fall back to random synthetic noise instead
of showing off the real patterns.

This script expands the daily aggregate demand + zone distribution into individual
order-level rows (matching the `orders` table schema) and loads them into the
database, so the LSTM forecasting and AI agent showcases actually reflect the
generated seasonality, growth trend, and holiday spikes.
"""

import argparse
import os
import random
import sqlite3
from datetime import datetime, timedelta

from generate_historical_data import generate_5_year_historical_data, generate_zone_level_data

DATABASE = 'smart_logistics.db'
NUM_PRODUCTS = 10

# Approximate NYC zone centers, matching the zone names used in generate_historical_data.py
ZONE_CENTERS = {
    'A': (40.7831, -73.9712),  # Manhattan
    'B': (40.6782, -73.9442),  # Brooklyn
    'C': (40.7282, -73.7949),  # Queens
    'D': (40.8448, -73.8648),  # Bronx
    'E': (40.5795, -74.1502),  # Staten Island
}

STREET_NAMES = ['Main St', 'Broadway', '5th Ave', 'Park Rd', 'Sunset Blvd', 'Union Sq']


def expand_day_to_orders(order_date, total_quantity, zone_weights):
    """Split one day's aggregate demand into several individual order rows,
    so SUM(quantity) for the day matches the generated pattern."""
    remaining = max(1, int(total_quantity))
    num_rows = max(1, min(remaining, random.randint(5, 15)))

    if remaining > num_rows:
        splits = sorted(random.sample(range(1, remaining), num_rows - 1))
    else:
        splits = []
    boundaries = [0] + splits + [remaining]
    quantities = [max(1, boundaries[i + 1] - boundaries[i]) for i in range(len(boundaries) - 1)]

    zones = list(zone_weights.keys())
    weights = list(zone_weights.values())

    rows = []
    for qty in quantities:
        zone = random.choices(zones, weights=weights, k=1)[0]
        lat_center, lon_center = ZONE_CENTERS[zone]
        delivery_time = datetime.strptime(order_date, '%Y-%m-%d') + timedelta(hours=random.randint(6, 22))
        rows.append((
            order_date,
            random.randint(1000, 9999),
            f'P{random.randint(1, NUM_PRODUCTS):03d}',
            qty,
            f'{random.choice(STREET_NAMES)} {random.randint(1, 999)}',
            round(lat_center + random.uniform(-0.03, 0.03), 6),
            round(lon_center + random.uniform(-0.03, 0.03), 6),
            delivery_time.strftime('%Y-%m-%d %H:%M:%S'),
            zone,
        ))
    return rows


def load_historical_data(db_path=DATABASE, days=730, keep_existing=False):
    """Generate historical data and load it into the orders table.

    Args:
        db_path: Path to the SQLite database file.
        days: Number of most recent days of history to load (default: 730 = 2 years).
        keep_existing: If True, append instead of clearing existing orders first.
    """
    print("Generating 5-year historical daily demand and zone distribution...")
    tmp_main_file = '_historical_orders_5years_tmp.csv'
    tmp_zones_file = '_historical_orders_by_zone_tmp.csv'
    df_main = generate_5_year_historical_data(tmp_main_file)
    df_zones = generate_zone_level_data(tmp_zones_file)

    df_main = df_main.tail(days).reset_index(drop=True)
    valid_dates = set(df_main['date'])
    df_zones = df_zones[df_zones['date'].isin(valid_dates)]

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    if not keep_existing:
        cursor.execute('DELETE FROM orders')
        print("Cleared existing orders.")

    total_rows = 0
    for _, day_row in df_main.iterrows():
        date_str = day_row['date']
        day_zone_rows = df_zones[df_zones['date'] == date_str]
        if day_zone_rows.empty:
            zone_weights = {z: 1 for z in ZONE_CENTERS}
        else:
            zone_weights = dict(zip(day_zone_rows['zone'], day_zone_rows['orders']))

        rows = expand_day_to_orders(date_str, day_row['orders'], zone_weights)
        cursor.executemany('''
            INSERT INTO orders (order_date, customer_id, product_id, quantity, delivery_address,
                                 latitude, longitude, delivery_time, zone)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', rows)
        total_rows += len(rows)

    conn.commit()
    total_in_db = cursor.execute('SELECT COUNT(*) FROM orders').fetchone()[0]
    conn.close()

    print(f"Inserted {total_rows} order rows spanning {len(df_main)} days.")
    print(f"Total orders now in database: {total_in_db}")
    print("LSTM forecasting and AI agents will now train on realistic seasonal/growth patterns.")

    for tmp_file in (tmp_main_file, tmp_zones_file):
        if os.path.exists(tmp_file):
            os.remove(tmp_file)

    return total_rows


def main():
    parser = argparse.ArgumentParser(
        description='Load generated historical demand data into smart_logistics.db'
    )
    parser.add_argument('--days', type=int, default=730,
                         help='Number of most recent days of history to load (default: 730 = 2 years)')
    parser.add_argument('--keep-existing', action='store_true',
                         help='Append to existing orders instead of clearing them first')
    parser.add_argument('--db', default=DATABASE, help='Path to the SQLite database file')
    args = parser.parse_args()

    load_historical_data(db_path=args.db, days=args.days, keep_existing=args.keep_existing)


if __name__ == '__main__':
    main()
