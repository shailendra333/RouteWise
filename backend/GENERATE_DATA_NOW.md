# ⚡ GENERATE 5 YEARS OF HISTORICAL DATA

## 🎯 ONE COMMAND

```bash
cd backend
generate_data.bat
```

---

## ✅ WHAT YOU GET

**4 files in `sample_data/`:**

1. **historical_orders_5years.csv** (1,826 days)
2. **historical_orders_by_product.csv** (10 products)
3. **historical_orders_by_zone.csv** (5 zones)
4. **data_summary.txt** (statistics)

**Total:** ~180,000 orders across 5 years (2021-2026)

---

## 📊 DATA INCLUDES

✅ Growth trends (15% per year)
✅ Seasonal patterns (Q4 peaks)
✅ Weekly patterns (weekday/weekend)
✅ Holiday spikes (Black Friday, Christmas)
✅ Random variations (realistic noise)

---

## 🎨 CUSTOM DATA

### Create configs:
```bash
python custom_data_generator.py --create-configs
```

### Use config:
```bash
python custom_data_generator.py --config config_growth.json
```

### Generate 10 variations:
```bash
python custom_data_generator.py --generate-multiple 10
```

---

## 📖 DOCUMENTATION

- **Quick start:** `DATA_README.md`
- **Full guide:** `DATA_GENERATION_GUIDE.md`
- **Complete summary:** `DATA_GENERATION_COMPLETE.md`

---

## ✅ VERIFY

```bash
dir sample_data
```

Should show 4 files!

---

## 🚀 USE IT

1. **Generate data:** `generate_data.bat`
2. **Go to app:** http://localhost:5173
3. **Navigate to:** "Demand Forecasting"
4. **Upload:** `historical_orders_5years.csv`
5. **Train LSTM** and get predictions!

---

**Status:** ✅ READY
**Time:** 30 seconds
**Action:** Run `generate_data.bat`

