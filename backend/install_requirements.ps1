# Quick installation script for updated requirements (Windows)
# Run this to install all dependencies including scipy

Write-Host "🚀 Installing Smart Logistics System Dependencies..." -ForegroundColor Green
Write-Host "==================================================" -ForegroundColor Green

# Upgrade pip first
Write-Host "`n📦 Upgrading pip..." -ForegroundColor Cyan
python -m pip install --upgrade pip

# Install all requirements
Write-Host "`n📦 Installing requirements..." -ForegroundColor Cyan
pip install -r requirements.txt

# Verify critical packages
Write-Host "`n✅ Verifying installations..." -ForegroundColor Yellow
try { python -c "import flask; print('✅ Flask:', flask.__version__)" } catch { Write-Host "❌ Flask failed" -ForegroundColor Red }
try { python -c "import numpy; print('✅ NumPy:', numpy.__version__)" } catch { Write-Host "❌ NumPy failed" -ForegroundColor Red }
try { python -c "import pandas; print('✅ Pandas:', pandas.__version__)" } catch { Write-Host "❌ Pandas failed" -ForegroundColor Red }
try { python -c "import sklearn; print('✅ scikit-learn:', sklearn.__version__)" } catch { Write-Host "❌ scikit-learn failed" -ForegroundColor Red }

# Verify Phase 2 & 3 requirements
Write-Host "`n🧠 Verifying Phase 2 & 3 requirements..." -ForegroundColor Yellow
try {
    python -c "import scipy; print('✅ SciPy:', scipy.__version__)"
} catch {
    Write-Host "❌ SciPy not installed - Phase 2 & 3 features will not work!" -ForegroundColor Red
}

# Verify GenAI requirements
Write-Host "`n🤖 Verifying GenAI requirements..." -ForegroundColor Yellow
try { python -c "import openai; print('✅ OpenAI:', openai.__version__)" } catch { Write-Host "❌ OpenAI failed" -ForegroundColor Red }

# Verify optional packages
Write-Host "`n📊 Verifying optional packages..." -ForegroundColor Yellow
try { python -c "import matplotlib; print('✅ Matplotlib:', matplotlib.__version__)" } catch { Write-Host "⚠️ Matplotlib not installed (optional)" -ForegroundColor Yellow }
try { python -c "import requests; print('✅ Requests:', requests.__version__)" } catch { Write-Host "⚠️ Requests not installed (optional)" -ForegroundColor Yellow }

Write-Host "`n==================================================" -ForegroundColor Green
Write-Host "✅ Installation complete!" -ForegroundColor Green
Write-Host "🚀 Ready to run: python app.py" -ForegroundColor Cyan

