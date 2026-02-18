"""
Customizable Historical Data Generator
Allows creating multiple variations of historical data with different parameters
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import json
import os
import argparse


class CustomDataGenerator:
    """
    Flexible data generator with customizable parameters
    """

    def __init__(self, config):
        self.config = config
        self.end_date = datetime.now()
        self.start_date = self.end_date - timedelta(days=365 * config['years'])

    def generate_dataset(self, output_file):
        """
        Generate dataset based on configuration
        """

        print(f"\n🚀 Generating custom dataset: {output_file}")
        print(f"   Years: {self.config['years']}")
        print(f"   Base orders: {self.config['base_orders_per_day']}")
        print(f"   Growth rate: {self.config['growth_rate']*100}%")

        date_range = pd.date_range(start=self.start_date, end=self.end_date, freq='D')
        orders_data = []

        for idx, date in enumerate(date_range):
            years_elapsed = idx / 365.25
            day_of_year = date.timetuple().tm_yday
            weekday = date.weekday()
            month = date.month
            day_of_month = date.day

            # Base calculation
            base = self.config['base_orders_per_day']

            # Growth trend
            growth = 1 + (self.config['growth_rate'] * years_elapsed)

            # Seasonality
            seasonal = 1
            if self.config['apply_seasonality']:
                seasonal = 1 + self.config['seasonality_strength'] * np.sin(
                    2 * np.pi * (day_of_year - 150) / 365
                )

            # Weekly pattern
            weekly = 1
            if self.config['apply_weekly_pattern']:
                if weekday < 5:
                    weekly = self.config['weekday_factor']
                else:
                    weekly = self.config['weekend_factor']

            # Holiday effects
            event = 1
            if self.config['apply_holiday_effects']:
                if month == 11 and 20 <= day_of_month <= 30:
                    event = self.config['holiday_spike']
                elif month == 12 and day_of_month <= 24:
                    event = self.config['holiday_spike'] * 0.9

            # Random noise
            noise = random.uniform(
                1 - self.config['noise_level'],
                1 + self.config['noise_level']
            )

            # Calculate final orders
            orders = int(base * growth * seasonal * weekly * event * noise)
            orders = max(orders, 1)

            orders_data.append({
                'date': date.strftime('%Y-%m-%d'),
                'orders': orders,
                'year': date.year,
                'month': date.month,
                'weekday': date.strftime('%A')
            })

        df = pd.DataFrame(orders_data)
        df.to_csv(output_file, index=False)

        print(f"   ✅ Generated {len(df)} days of data")
        print(f"   📊 Total orders: {df['orders'].sum():,}")
        print(f"   📈 Avg orders/day: {df['orders'].mean():.2f}")
        print(f"   💾 Saved to: {output_file}")

        return df


def load_config(config_file):
    """
    Load configuration from JSON file
    """

    if os.path.exists(config_file):
        with open(config_file, 'r') as f:
            return json.load(f)
    else:
        return get_default_config()


def get_default_config():
    """
    Get default configuration
    """

    return {
        "years": 5,
        "base_orders_per_day": 100,
        "growth_rate": 0.15,
        "apply_seasonality": True,
        "seasonality_strength": 0.3,
        "apply_weekly_pattern": True,
        "weekday_factor": 1.2,
        "weekend_factor": 0.6,
        "apply_holiday_effects": True,
        "holiday_spike": 1.8,
        "noise_level": 0.2
    }


def create_sample_configs():
    """
    Create sample configuration files for different scenarios
    """

    print("\n🔧 Creating sample configuration files...")

    configs = {
        'config_stable.json': {
            "name": "Stable Business",
            "years": 5,
            "base_orders_per_day": 120,
            "growth_rate": 0.05,
            "apply_seasonality": True,
            "seasonality_strength": 0.15,
            "apply_weekly_pattern": True,
            "weekday_factor": 1.1,
            "weekend_factor": 0.8,
            "apply_holiday_effects": True,
            "holiday_spike": 1.3,
            "noise_level": 0.15
        },
        'config_growth.json': {
            "name": "High Growth Business",
            "years": 5,
            "base_orders_per_day": 50,
            "growth_rate": 0.35,
            "apply_seasonality": True,
            "seasonality_strength": 0.25,
            "apply_weekly_pattern": True,
            "weekday_factor": 1.3,
            "weekend_factor": 0.7,
            "apply_holiday_effects": True,
            "holiday_spike": 2.0,
            "noise_level": 0.25
        },
        'config_seasonal.json': {
            "name": "Highly Seasonal Business",
            "years": 5,
            "base_orders_per_day": 100,
            "growth_rate": 0.10,
            "apply_seasonality": True,
            "seasonality_strength": 0.6,
            "apply_weekly_pattern": True,
            "weekday_factor": 1.2,
            "weekend_factor": 0.5,
            "apply_holiday_effects": True,
            "holiday_spike": 2.5,
            "noise_level": 0.20
        },
        'config_steady.json': {
            "name": "Steady State Business",
            "years": 3,
            "base_orders_per_day": 150,
            "growth_rate": 0.02,
            "apply_seasonality": False,
            "seasonality_strength": 0.0,
            "apply_weekly_pattern": True,
            "weekday_factor": 1.15,
            "weekend_factor": 0.85,
            "apply_holiday_effects": False,
            "holiday_spike": 1.0,
            "noise_level": 0.10
        }
    }

    for filename, config in configs.items():
        with open(filename, 'w') as f:
            json.dump(config, f, indent=2)
        print(f"   ✅ Created {filename} - {config['name']}")

    print("\n   Sample configs created!")


def generate_multiple_datasets(num_datasets=5, base_config=None):
    """
    Generate multiple datasets with varied parameters
    """

    print(f"\n🎲 Generating {num_datasets} varied datasets...")

    if base_config is None:
        base_config = get_default_config()

    for i in range(num_datasets):
        # Vary parameters
        config = base_config.copy()
        config['base_orders_per_day'] = random.randint(50, 200)
        config['growth_rate'] = random.uniform(0.0, 0.3)
        config['seasonality_strength'] = random.uniform(0.1, 0.5)
        config['noise_level'] = random.uniform(0.1, 0.3)

        output_file = f'dataset_variation_{i+1}.csv'
        generator = CustomDataGenerator(config)
        generator.generate_dataset(output_file)

    print(f"\n✅ Generated {num_datasets} datasets with varied parameters")


def main():
    """
    Main function with command-line interface
    """

    parser = argparse.ArgumentParser(description='Generate custom historical order data')
    parser.add_argument('--config', type=str, help='Configuration file (JSON)')
    parser.add_argument('--output', type=str, default='custom_historical_data.csv',
                       help='Output filename')
    parser.add_argument('--create-configs', action='store_true',
                       help='Create sample configuration files')
    parser.add_argument('--generate-multiple', type=int, metavar='N',
                       help='Generate N datasets with varied parameters')

    args = parser.parse_args()

    # Create sample_data directory
    os.makedirs('sample_data', exist_ok=True)
    os.chdir('sample_data')

    print("=" * 60)
    print("  CUSTOM HISTORICAL DATA GENERATOR")
    print("=" * 60)

    # Create sample configs if requested
    if args.create_configs:
        create_sample_configs()
        return

    # Generate multiple datasets if requested
    if args.generate_multiple:
        generate_multiple_datasets(args.generate_multiple)
        return

    # Load configuration
    if args.config:
        print(f"\n📋 Loading configuration from: {args.config}")
        config = load_config(args.config)
    else:
        print("\n📋 Using default configuration")
        config = get_default_config()

    # Generate dataset
    generator = CustomDataGenerator(config)
    df = generator.generate_dataset(args.output)

    # Show preview
    print("\n📊 Preview of generated data:")
    print(df.head(10))
    print("\n...")
    print(df.tail(10))

    print("\n✅ Generation complete!")


if __name__ == "__main__":
    main()

