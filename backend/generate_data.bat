@echo off
echo ============================================
echo   GENERATING HISTORICAL DATA
echo ============================================
echo.

cd /d "%~dp0"

echo Running data generator...
python generate_historical_data.py

echo.
echo ============================================
echo   COMPLETE!
echo ============================================
echo.
echo Check the sample_data/ folder for generated files:
echo   - historical_orders_5years.csv
echo   - historical_orders_by_product.csv
echo   - historical_orders_by_zone.csv
echo   - data_summary.txt
echo.
pause

