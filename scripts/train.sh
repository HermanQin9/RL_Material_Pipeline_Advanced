#!/bin/bash
# Quick training script for PPO pipeline
# Usage: ./train.sh [episodes] [mode]

set -e

# Default values
EPISODES=${1:-50}
MODE=${2:-test}

echo "🎯 Starting PPO Training"
echo "======================="
echo "Episodes: $EPISODES"
echo "Mode: $MODE"
echo ""

# Set environment based on mode
if [ "$MODE" = "production" ] || [ "$MODE" = "prod" ]; then
    export PIPELINE_TEST=0
    echo "📊 Running in PRODUCTION mode (4K dataset)"
else
    export PIPELINE_TEST=1
    echo "🧪 Running in TEST mode (200 samples)"
fi

# Check if virtual environment is activated
if [ -z "$VIRTUAL_ENV" ]; then
    echo "⚠️  Virtual environment not activated"
    echo "Attempting to activate..."
    source venv/bin/activate || . venv/Scripts/activate || {
        echo "❌ Failed to activate virtual environment"
        echo "Please run: source venv/bin/activate"
        exit 1
    }
fi

# Check required environment variables
if [ -z "$MP_API_KEY" ]; then
    echo "⚠️  MP_API_KEY not set"
    echo "Using default from config.py"
fi

# Run training
echo ""
echo "🚀 Launching training..."
python scripts/train_ppo.py --episodes $EPISODES

# Check if training completed successfully
if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Training completed successfully!"
    echo "📁 Check logs/ for training curves"
    echo "💾 Check models/ for saved models"
else
    echo ""
    echo "❌ Training failed"
    exit 1
fi
