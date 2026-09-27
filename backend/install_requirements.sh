#!/bin/bash
# Quick installation script for updated requirements
# Run this to install all dependencies including scipy

echo "🚀 Installing Smart Logistics System Dependencies..."
echo "=================================================="

# Upgrade pip first
echo "📦 Upgrading pip..."
python -m pip install --upgrade pip

# Install all requirements
echo "📦 Installing requirements..."
pip install -r requirements.txt

# Verify critical packages
echo ""
echo "✅ Verifying installations..."
python -c "import flask; print('✅ Flask:', flask.__version__)"
python -c "import numpy; print('✅ NumPy:', numpy.__version__)"
python -c "import pandas; print('✅ Pandas:', pandas.__version__)"
python -c "import sklearn; print('✅ scikit-learn:', sklearn.__version__)"

# Verify Phase 2 & 3 requirements
echo ""
echo "🧠 Verifying Phase 2 & 3 requirements..."
python -c "import scipy; print('✅ SciPy:', scipy.__version__)" || echo "❌ SciPy not installed - Phase 2 & 3 features will not work!"

# Verify GenAI requirements
echo ""
echo "🤖 Verifying GenAI requirements..."
python -c "import openai; print('✅ OpenAI:', openai.__version__)"

# Verify optional packages
echo ""
echo "📊 Verifying optional packages..."
python -c "import matplotlib; print('✅ Matplotlib:', matplotlib.__version__)" || echo "⚠️ Matplotlib not installed (optional)"
python -c "import requests; print('✅ Requests:', requests.__version__)" || echo "⚠️ Requests not installed (optional)"

echo ""
echo "=================================================="
echo "✅ Installation complete!"
echo "🚀 Ready to run: python app.py"

