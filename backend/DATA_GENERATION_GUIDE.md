# 📊 Historical Data Generation Guide

## 🎯 Overview

This guide explains how to generate historical order data for demand forecasting and LSTM model training.

---

## 📁 Generated Files

### Main Generator (`generate_historical_data.py`)

Generates **4 files** with 5 years of data:

1. **`historical_orders_5years.csv`** - Daily aggregated data
   - 1,825+ days of historical orders
   - Includes seasonality, trends, and patterns
   - Perfect for LSTM training

2. **`historical_orders_by_product.csv`** - Product-level breakdown
   - Data for 10 products
   - Individual product trends
   - For granular forecasting

3. **`historical_orders_by_zone.csv`** - Geographic breakdown
   - Data for 5 NYC zones (A-E)
   - Regional patterns
   - For location-based forecasting

4. **`data_summary.txt`** - Statistical summary
   - Key metrics and insights
   - Yearly/quarterly/weekly patterns
   - Data validation

---

## 🚀 Quick Start

### Option 1: Run the Main Generator

**Windows:**
```bash
cd backend
generate_data.bat
```

**Or directly:**
```bash
cd backend
python generate_historical_data.py
```

**Output:**
```
✅ Generated 1,826 days of historical data
📅 Date range: 2021-02-13 to 2026-02-13
📊 Total orders: 234,567
📈 Average orders per day: 128.45
💾 Files saved in: sample_data/
```

---

## 🎨 Custom Data Generation

### Using the Custom Generator

The `custom_data_generator.py` provides flexible data generation with configurable parameters.

#### 1. Generate with Default Settings

```bash
python custom_data_generator.py --output my_custom_data.csv
```

#### 2. Create Sample Configuration Files

```bash
python custom_data_generator.py --create-configs
```

This creates 4 sample configs:
- `config_stable.json` - Stable business (5% growth)
- `config_growth.json` - High growth (35% growth)
- `config_seasonal.json` - Highly seasonal business
- `config_steady.json` - Steady state business

#### 3. Use a Configuration File

```bash
python custom_data_generator.py --config config_growth.json --output high_growth_data.csv
```

#### 4. Generate Multiple Variations

```bash
python custom_data_generator.py --generate-multiple 10
```

Generates 10 datasets with randomized parameters:
- `dataset_variation_1.csv`
- `dataset_variation_2.csv`
- ... etc.

---

## 📋 Configuration Parameters

### Sample Configuration File (`config.json`)

```json
{
  "years": 5,
  "base_orders_per_day": 100,
  "growth_rate": 0.15,
  "apply_seasonality": true,
  "seasonality_strength": 0.3,
  "apply_weekly_pattern": true,
  "weekday_factor": 1.2,
  "weekend_factor": 0.6,
  "apply_holiday_effects": true,
  "holiday_spike": 1.8,
  "noise_level": 0.2
}
```

### Parameter Descriptions

| Parameter | Description | Range | Example |
|-----------|-------------|-------|---------|
| `years` | Years of historical data | 1-10 | 5 |
| `base_orders_per_day` | Starting daily orders | 10-500 | 100 |
| `growth_rate` | Annual growth rate | -0.2 to 0.5 | 0.15 (15%) |
| `apply_seasonality` | Enable seasonal patterns | true/false | true |
| `seasonality_strength` | Strength of seasons | 0.0-1.0 | 0.3 |
| `apply_weekly_pattern` | Enable weekly patterns | true/false | true |
| `weekday_factor` | Weekday multiplier | 0.5-2.0 | 1.2 |
| `weekend_factor` | Weekend multiplier | 0.3-1.5 | 0.6 |
| `apply_holiday_effects` | Enable holiday spikes | true/false | true |
| `holiday_spike` | Holiday multiplier | 1.0-3.0 | 1.8 |
| `noise_level` | Random variation | 0.0-0.5 | 0.2 (±20%) |

---

## 📊 Data Patterns Included

### 1. Growth Trend
- Simulates business growth over time
- Configurable growth rate (e.g., 15% per year)
- Compounds annually

### 2. Seasonal Patterns
- **Q4 (Oct-Dec)**: Highest orders (holiday season)
- **Q1 (Jan-Mar)**: Above average (New Year sales)
- **Q2 (Apr-Jun)**: Moderate
- **Q3 (Jul-Sep)**: Lower (summer slowdown)

### 3. Weekly Patterns
- **Mon-Fri**: Higher orders (business days)
- **Saturday**: Moderate
- **Sunday**: Lowest

### 4. Holiday Spikes
- **Black Friday**: +80% spike
- **Christmas**: +60% spike
- **New Year**: +40% spike
- **Back to School**: +30% spike

### 5. Random Noise
- ±20% daily variation
- Simulates real-world unpredictability

---

## 📈 Sample Output Data

### `historical_orders_5years.csv`

```csv
date,orders,year,month,day,weekday,is_weekend,quarter,orders_7day_avg,orders_30day_avg
2021-02-13,95,2021,2,13,Saturday,1,1,95.00,95.00
2021-02-14,68,2021,2,14,Sunday,1,1,81.50,81.50
2021-02-15,112,2021,2,15,Monday,0,1,91.67,91.67
2021-02-16,118,2021,2,16,Tuesday,0,1,98.25,98.25
2021-02-17,125,2021,2,17,Wednesday,0,1,103.60,103.60
...
2026-02-13,186,2026,2,13,Friday,0,1,178.43,175.82
```

### `historical_orders_by_product.csv`

```csv
date,product_id,orders,revenue
2021-02-13,PROD-001,18,1245.67
2021-02-13,PROD-002,24,3421.89
2021-02-13,PROD-003,31,2789.45
...
```

### `historical_orders_by_zone.csv`

```csv
date,zone,zone_name,orders
2021-02-13,A,Manhattan,35
2021-02-13,B,Brooklyn,28
2021-02-13,C,Queens,22
...
```

---

## 🎯 Use Cases

### 1. LSTM Model Training

Use `historical_orders_5years.csv`:
```python
# Load data
df = pd.read_csv('sample_data/historical_orders_5years.csv')

# Prepare for LSTM
data = df['orders'].values
# Train model...
```

### 2. Product-Specific Forecasting

Use `historical_orders_by_product.csv`:
```python
# Filter for specific product
product_data = df[df['product_id'] == 'PROD-001']
# Forecast this product...
```

### 3. Regional Analysis

Use `historical_orders_by_zone.csv`:
```python
# Analyze zone patterns
zone_a = df[df['zone'] == 'A']
# Zone-specific forecasting...
```

### 4. A/B Testing Different Scenarios

Generate multiple datasets:
```bash
# Test stable vs growth scenarios
python custom_data_generator.py --config config_stable.json --output stable.csv
python custom_data_generator.py --config config_growth.json --output growth.csv
```

---

## 🔄 Regenerating Data

### When to Regenerate

- Testing different forecasting algorithms
- Evaluating model sensitivity
- Creating training/validation splits
- Simulating different business scenarios

### How to Regenerate

**Option 1: Quick regeneration**
```bash
cd backend
generate_data.bat
```

**Option 2: With custom parameters**
1. Edit a config file (e.g., `config_custom.json`)
2. Run: `python custom_data_generator.py --config config_custom.json`

**Option 3: Batch generation**
```bash
# Generate 20 variations for testing
python custom_data_generator.py --generate-multiple 20
```

---

## 📝 Data Quality

### Validation Checks

The generated data includes:
- ✅ No missing values
- ✅ All dates sequential
- ✅ Realistic order volumes (10-500 per day)
- ✅ Proper date formatting (YYYY-MM-DD)
- ✅ Consistent patterns
- ✅ Statistical validity

### Summary Statistics

Check `data_summary.txt` for:
- Total orders
- Average orders per day
- Min/max orders
- Yearly breakdown
- Seasonal patterns
- Weekly patterns

---

## 🎨 Customization Examples

### Example 1: E-commerce Business

```json
{
  "years": 3,
  "base_orders_per_day": 200,
  "growth_rate": 0.25,
  "seasonality_strength": 0.5,
  "holiday_spike": 2.5,
  "weekday_factor": 1.3,
  "weekend_factor": 0.4
}
```

### Example 2: B2B Business

```json
{
  "years": 5,
  "base_orders_per_day": 80,
  "growth_rate": 0.10,
  "seasonality_strength": 0.2,
  "holiday_spike": 1.1,
  "weekday_factor": 1.5,
  "weekend_factor": 0.2
}
```

### Example 3: Retail Store

```json
{
  "years": 4,
  "base_orders_per_day": 150,
  "growth_rate": 0.08,
  "seasonality_strength": 0.4,
  "holiday_spike": 2.0,
  "weekday_factor": 1.2,
  "weekend_factor": 1.8
}
```

---

## 🛠️ Advanced Usage

### Generate Data Programmatically

```python
from custom_data_generator import CustomDataGenerator

config = {
    "years": 5,
    "base_orders_per_day": 120,
    "growth_rate": 0.18,
    "apply_seasonality": True,
    "seasonality_strength": 0.35,
    "noise_level": 0.15
}

generator = CustomDataGenerator(config)
df = generator.generate_dataset('my_dataset.csv')

print(f"Generated {len(df)} days of data")
print(f"Total orders: {df['orders'].sum():,}")
```

### Combine Multiple Datasets

```python
import pandas as pd
import glob

# Load all variations
files = glob.glob('dataset_variation_*.csv')
dfs = [pd.read_csv(f) for f in files]

# Combine for ensemble training
combined = pd.concat(dfs, ignore_index=True)
combined.to_csv('combined_dataset.csv', index=False)
```

---

## 📞 Troubleshooting

### Issue: Script not running
**Solution:**
```bash
# Ensure you're in backend directory
cd backend

# Check Python is installed
python --version

# Install required packages
pip install pandas numpy
```

### Issue: No output files
**Solution:**
```bash
# Check if sample_data folder was created
dir sample_data

# Run with verbose output
python generate_historical_data.py
```

### Issue: Data looks unrealistic
**Solution:**
- Adjust parameters in config file
- Check `seasonality_strength` (0.2-0.4 recommended)
- Check `noise_level` (0.15-0.25 recommended)
- Verify `growth_rate` is reasonable (0.05-0.20)

---

## ✅ Quick Reference

### Generate Default 5-Year Data
```bash
cd backend && generate_data.bat
```

### Generate Custom Data
```bash
python custom_data_generator.py --config my_config.json --output my_data.csv
```

### Create Config Templates
```bash
python custom_data_generator.py --create-configs
```

### Generate Multiple Variations
```bash
python custom_data_generator.py --generate-multiple 10
```

### View Generated Data
```bash
# In Python
import pandas as pd
df = pd.read_csv('sample_data/historical_orders_5years.csv')
print(df.head())
print(df.describe())
```

---

## 🎉 Success!

After running the generators, you'll have:
- ✅ 5 years of realistic historical data
- ✅ Product and zone breakdowns
- ✅ Statistical summaries
- ✅ Multiple dataset variations
- ✅ Ready for LSTM training!

**Use this data to:**
1. Train demand forecasting models
2. Test different algorithms
3. Validate predictions
4. Demo the system
5. Develop new features

---

**Generated data is in:** `backend/sample_data/`

**Next step:** Use the data with the LSTM forecasting model in the Demand Forecasting page!

