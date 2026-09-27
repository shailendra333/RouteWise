# 🎯 QUICK START - Generate Historical Data

## ⚡ Generate 5 Years of Data (One Command)

```bash
cd backend
generate_data.bat
```

**Or:**
```bash
python generate_historical_data.py
```

---

## 📁 What You Get

✅ **4 files created** in `sample_data/`:

1. **`historical_orders_5years.csv`** (1,826 days)
   - Daily order totals
   - 5 years: 2021-02-13 to 2026-02-13
   - ~180,000 total orders
   - Includes trends, seasonality, patterns

2. **`historical_orders_by_product.csv`** (18,260 records)
   - 10 products
   - Product-specific patterns
   - Individual trends

3. **`historical_orders_by_zone.csv`** (9,130 records)
   - 5 NYC zones (A-E)
   - Geographic breakdown
   - Regional patterns

4. **`data_summary.txt`**
   - Statistical summary
   - Yearly/quarterly/weekly insights

---

## 🎨 Generate Custom Data

### Create Sample Configs
```bash
python custom_data_generator.py --create-configs
```

Creates 4 templates:
- `config_stable.json` - Stable 5% growth
- `config_growth.json` - High 35% growth  
- `config_seasonal.json` - Heavy seasonality
- `config_steady.json` - Steady state

### Use a Config
```bash
python custom_data_generator.py --config config_growth.json --output growth_data.csv
```

### Generate Multiple Variations
```bash
python custom_data_generator.py --generate-multiple 10
```

---

## 📊 Data Features

✅ **Growth Trends** - 15% annual growth (configurable)
✅ **Seasonality** - Q4 peaks, summer lows
✅ **Weekly Patterns** - Higher Mon-Fri, lower weekends
✅ **Holiday Spikes** - Black Friday, Christmas, etc.
✅ **Random Noise** - ±20% daily variation
✅ **Realistic Volumes** - 50-200 orders/day

---

## 🎯 Use Cases

1. **LSTM Model Training** - Use `historical_orders_5years.csv`
2. **Product Forecasting** - Use `historical_orders_by_product.csv`
3. **Regional Analysis** - Use `historical_orders_by_zone.csv`
4. **A/B Testing** - Generate multiple scenarios

---

## 📖 Full Documentation

See `DATA_GENERATION_GUIDE.md` for:
- Complete parameter reference
- Configuration examples
- Advanced usage
- Troubleshooting

---

## ✅ Quick Check

After generation, verify:
```bash
dir sample_data
```

Should show 4 files created!

---

**Ready to train your LSTM model with 5 years of realistic data!** 🚀

