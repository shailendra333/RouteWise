"""
Generate Historical Order Data for Demand Forecasting
Creates realistic 5-year historical data for LSTM training
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import os


def generate_5_year_historical_data(output_file='historical_orders_5years.csv'):
    """
    Generate 5 years of historical order data with realistic patterns

    Patterns included:
    - Seasonal trends (higher in Q4, lower in summer)
    - Weekly patterns (higher Mon-Fri, lower weekends)
    - Growth trend (business growing over time)
    - Random variations
    - Special events (holidays, promotions)
    """

    print("🚀 Generating 5 years of historical order data...")

    # Date range: 5 years back from today
    end_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    start_date = end_date - timedelta(days=365 * 5)

    # Generate daily data
    date_range = pd.date_range(start=start_date, end=end_date, freq='D')

    orders_data = []

    # Base parameters
    base_orders_per_day = 80  # Starting point 5 years ago
    growth_rate = 0.15  # 15% annual growth

    for idx, date in enumerate(date_range):
        # Calculate day of year for seasonality
        day_of_year = date.timetuple().tm_yday

        # Years since start for growth trend
        years_elapsed = idx / 365.25

        # 1. Growth trend (15% per year)
        growth_factor = 1 + (growth_rate * years_elapsed)

        # 2. Seasonal pattern (higher in Q4, lower in summer)
        # Using sine wave with peak in November (day ~320)
        seasonal_factor = 1 + 0.3 * np.sin(2 * np.pi * (day_of_year - 150) / 365)

        # 3. Weekly pattern (higher on weekdays)
        weekday = date.weekday()
        if weekday < 5:  # Monday-Friday
            weekly_factor = 1.2
        elif weekday == 5:  # Saturday
            weekly_factor = 0.7
        else:  # Sunday
            weekly_factor = 0.5

        # 4. Monthly pattern (higher at end/beginning of month)
        day_of_month = date.day
        if day_of_month <= 5 or day_of_month >= 25:
            monthly_factor = 1.15
        else:
            monthly_factor = 1.0

        # 5. Holiday/Event spikes
        event_factor = 1.0
        month = date.month

        # Black Friday / Cyber Monday (late November)
        if month == 11 and 20 <= day_of_month <= 30:
            event_factor = 1.8

        # Christmas shopping (December)
        elif month == 12 and day_of_month <= 24:
            event_factor = 1.6

        # New Year sales (early January)
        elif month == 1 and day_of_month <= 10:
            event_factor = 1.4

        # Back to school (late August)
        elif month == 8 and day_of_month >= 15:
            event_factor = 1.3

        # Spring sales (March-April)
        elif month in [3, 4]:
            event_factor = 1.2

        # Summer slowdown (July-August)
        elif month in [7, 8]:
            event_factor = 0.85

        # 6. Calculate expected orders
        expected_orders = (
            base_orders_per_day *
            growth_factor *
            seasonal_factor *
            weekly_factor *
            monthly_factor *
            event_factor
        )

        # 7. Add random noise (±20%)
        noise_factor = random.uniform(0.8, 1.2)
        actual_orders = int(expected_orders * noise_factor)

        # Ensure minimum orders
        actual_orders = max(actual_orders, 10)

        orders_data.append({
            'date': date.strftime('%Y-%m-%d'),
            'orders': actual_orders,
            'year': date.year,
            'month': date.month,
            'day': date.day,
            'weekday': date.strftime('%A'),
            'is_weekend': 1 if weekday >= 5 else 0,
            'quarter': (month - 1) // 3 + 1
        })

    # Create DataFrame
    df = pd.DataFrame(orders_data)

    # Add rolling averages for context
    df['orders_7day_avg'] = df['orders'].rolling(window=7, min_periods=1).mean().round(2)
    df['orders_30day_avg'] = df['orders'].rolling(window=30, min_periods=1).mean().round(2)

    # Save to CSV
    df.to_csv(output_file, index=False)

    print(f"\n✅ Generated {len(df)} days of historical data")
    print(f"📅 Date range: {df['date'].min()} to {df['date'].max()}")
    print(f"📊 Total orders: {df['orders'].sum():,}")
    print(f"📈 Average orders per day: {df['orders'].mean():.2f}")
    print(f"📉 Min orders in a day: {df['orders'].min()}")
    print(f"📈 Max orders in a day: {df['orders'].max()}")
    print(f"\n💾 Saved to: {output_file}")

    return df


def generate_product_level_data(output_file='historical_orders_by_product.csv', num_products=10):
    """
    Generate product-level historical data for more granular forecasting
    """

    print(f"\n🚀 Generating product-level data for {num_products} products...")

    end_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    start_date = end_date - timedelta(days=365 * 5)
    date_range = pd.date_range(start=start_date, end=end_date, freq='D')

    products = [f'PROD-{str(i+1).zfill(3)}' for i in range(num_products)]

    product_data = []

    for product_id in products:
        # Each product has different characteristics
        product_index = int(product_id.split('-')[1])

        # Base demand varies by product (20-150 orders/day)
        base_demand = 20 + (product_index * 10)

        # Growth rate varies (-5% to +25%)
        growth_rate = -0.05 + (product_index * 0.03)

        # Seasonality strength varies
        seasonality_strength = 0.1 + (product_index * 0.03)

        for idx, date in enumerate(date_range):
            years_elapsed = idx / 365.25
            day_of_year = date.timetuple().tm_yday
            weekday = date.weekday()

            # Apply patterns
            growth_factor = 1 + (growth_rate * years_elapsed)
            seasonal_factor = 1 + seasonality_strength * np.sin(2 * np.pi * (day_of_year - 150) / 365)
            weekly_factor = 1.1 if weekday < 5 else 0.7
            noise = random.uniform(0.7, 1.3)

            orders = int(base_demand * growth_factor * seasonal_factor * weekly_factor * noise)
            orders = max(orders, 1)

            product_data.append({
                'date': date.strftime('%Y-%m-%d'),
                'product_id': product_id,
                'orders': orders,
                'revenue': orders * random.uniform(25, 150)  # Random price per order
            })

    df = pd.DataFrame(product_data)
    df.to_csv(output_file, index=False)

    print(f"✅ Generated data for {num_products} products")
    print(f"📊 Total records: {len(df):,}")
    print(f"💾 Saved to: {output_file}")

    return df


def generate_zone_level_data(output_file='historical_orders_by_zone.csv'):
    """
    Generate zone-level historical data for regional forecasting
    """

    print("\n🚀 Generating zone-level data...")

    end_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    start_date = end_date - timedelta(days=365 * 5)
    date_range = pd.date_range(start=start_date, end=end_date, freq='D')

    zones = ['A', 'B', 'C', 'D', 'E']
    zone_names = {
        'A': 'Manhattan',
        'B': 'Brooklyn',
        'C': 'Queens',
        'D': 'Bronx',
        'E': 'Staten Island'
    }

    zone_data = []

    for zone in zones:
        # Each zone has different characteristics
        zone_index = ord(zone) - ord('A')

        # Base orders per zone (Manhattan highest, Staten Island lowest)
        base_orders = [100, 85, 80, 60, 45][zone_index]
        growth_rate = [0.18, 0.15, 0.16, 0.12, 0.10][zone_index]

        for idx, date in enumerate(date_range):
            years_elapsed = idx / 365.25
            day_of_year = date.timetuple().tm_yday
            weekday = date.weekday()

            growth_factor = 1 + (growth_rate * years_elapsed)
            seasonal_factor = 1 + 0.25 * np.sin(2 * np.pi * (day_of_year - 150) / 365)
            weekly_factor = 1.15 if weekday < 5 else 0.65
            noise = random.uniform(0.8, 1.2)

            orders = int(base_orders * growth_factor * seasonal_factor * weekly_factor * noise)

            zone_data.append({
                'date': date.strftime('%Y-%m-%d'),
                'zone': zone,
                'zone_name': zone_names[zone],
                'orders': orders
            })

    df = pd.DataFrame(zone_data)
    df.to_csv(output_file, index=False)

    print(f"✅ Generated data for {len(zones)} zones")
    print(f"📊 Total records: {len(df):,}")
    print(f"💾 Saved to: {output_file}")

    return df


def generate_summary_statistics(df, output_file='data_summary.txt'):
    """
    Generate summary statistics and insights about the generated data
    """

    print("\n📊 Generating summary statistics...")

    summary = []
    summary.append("=" * 60)
    summary.append("HISTORICAL ORDER DATA SUMMARY")
    summary.append("=" * 60)
    summary.append(f"\nGenerated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    summary.append(f"\nDate Range: {df['date'].min()} to {df['date'].max()}")
    summary.append(f"Total Days: {len(df):,}")
    summary.append(f"\nTotal Orders: {df['orders'].sum():,}")
    summary.append(f"Average Orders/Day: {df['orders'].mean():.2f}")
    summary.append(f"Median Orders/Day: {df['orders'].median():.2f}")
    summary.append(f"Std Dev: {df['orders'].std():.2f}")
    summary.append(f"Min Orders/Day: {df['orders'].min()}")
    summary.append(f"Max Orders/Day: {df['orders'].max()}")

    summary.append("\n" + "=" * 60)
    summary.append("YEARLY BREAKDOWN")
    summary.append("=" * 60)

    yearly = df.groupby('year')['orders'].agg(['sum', 'mean', 'count'])
    for year, row in yearly.iterrows():
        summary.append(f"\n{year}:")
        summary.append(f"  Total Orders: {row['sum']:,}")
        summary.append(f"  Avg Orders/Day: {row['mean']:.2f}")
        summary.append(f"  Days: {row['count']}")

    summary.append("\n" + "=" * 60)
    summary.append("SEASONAL PATTERNS")
    summary.append("=" * 60)

    quarterly = df.groupby('quarter')['orders'].mean()
    quarters = {1: 'Q1 (Jan-Mar)', 2: 'Q2 (Apr-Jun)', 3: 'Q3 (Jul-Sep)', 4: 'Q4 (Oct-Dec)'}
    for q, avg in quarterly.items():
        summary.append(f"\n{quarters[q]}: {avg:.2f} orders/day")

    summary.append("\n" + "=" * 60)
    summary.append("WEEKLY PATTERNS")
    summary.append("=" * 60)

    weekly = df.groupby('weekday')['orders'].mean()
    weekday_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    for day in weekday_order:
        if day in weekly.index:
            summary.append(f"{day}: {weekly[day]:.2f} orders/day")

    summary_text = '\n'.join(summary)

    with open(output_file, 'w') as f:
        f.write(summary_text)

    print(summary_text)
    print(f"\n💾 Summary saved to: {output_file}")


def main():
    """
    Main function to generate all sample data files
    """

    print("=" * 60)
    print("  HISTORICAL ORDER DATA GENERATOR")
    print("  For Demand Forecasting & LSTM Training")
    print("=" * 60)
    print()

    # Create sample_data directory if it doesn't exist
    os.makedirs('sample_data', exist_ok=True)
    os.chdir('sample_data')

    # 1. Generate main 5-year historical data
    df_main = generate_5_year_historical_data('historical_orders_5years.csv')

    # 2. Generate product-level data
    df_products = generate_product_level_data('historical_orders_by_product.csv', num_products=10)

    # 3. Generate zone-level data
    df_zones = generate_zone_level_data('historical_orders_by_zone.csv')

    # 4. Generate summary statistics
    generate_summary_statistics(df_main, 'data_summary.txt')

    print("\n" + "=" * 60)
    print("✅ ALL FILES GENERATED SUCCESSFULLY!")
    print("=" * 60)
    print("\nGenerated files:")
    print("  1. historical_orders_5years.csv        - Daily totals (5 years)")
    print("  2. historical_orders_by_product.csv    - Product-level data")
    print("  3. historical_orders_by_zone.csv       - Zone-level data")
    print("  4. data_summary.txt                     - Statistical summary")
    print("\nAll files saved in: sample_data/")
    print("\n🎯 Ready for LSTM demand forecasting training!")
    print()


if __name__ == "__main__":
    main()

