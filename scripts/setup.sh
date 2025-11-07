#!/bin/bash
# Setup script for MatFormPPO project
# Sets up Python environment and dependencies

set -e  # Exit on error

echo "🚀 MatFormPPO Environment Setup"
echo "================================"

# Check Python version
echo "📍 Checking Python version..."
python_version=$(python --version 2>&1 | awk '{print $2}')
echo "✓ Python $python_version detected"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python -m venv venv
    echo "✓ Virtual environment created"
else
    echo "✓ Virtual environment already exists"
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate || . venv/Scripts/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
python -m pip install --upgrade pip --quiet

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt --quiet

# Create necessary directories
echo "📁 Creating data directories..."
mkdir -p data/raw data/processed models logs

# Verify installation
echo "✅ Verifying installation..."
python -c "
import torch
import pandas
import numpy
import sklearn
print('✓ Core packages installed successfully')
"

echo ""
echo "🎉 Setup complete!"
echo ""
echo "Next steps:"
echo "  1. Activate environment: source venv/bin/activate"
echo "  2. Set API key: export MP_API_KEY='your_key'"
echo "  3. Run training: python scripts/train_ppo.py"
echo ""
