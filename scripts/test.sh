#!/bin/bash
# Run all tests with coverage
# Usage: ./test.sh [pattern]

set -e

PATTERN=${1:-""}

echo "🧪 Running Test Suite"
echo "===================="

# Activate environment if needed
if [ -z "$VIRTUAL_ENV" ]; then
    source venv/bin/activate || . venv/Scripts/activate
fi

# Set test environment
export PIPELINE_TEST=1
export PYTEST_DISABLE_PLUGIN_AUTOLOAD=1

echo "📋 Test Configuration:"
echo "   - Test mode: ON"
echo "   - Plugin autoload: DISABLED"
echo ""

# Run tests based on pattern
if [ -z "$PATTERN" ]; then
    echo "🔍 Running all tests..."
    pytest tests/ -v --tb=short --maxfail=10
else
    echo "🔍 Running tests matching: $PATTERN"
    pytest tests/ -k "$PATTERN" -v --tb=short
fi

# Run integration test
echo ""
echo "🔗 Running integration test..."
python test_n4_gnn_integration.py

# Summary
if [ $? -eq 0 ]; then
    echo ""
    echo "✅ All tests passed!"
else
    echo ""
    echo "❌ Some tests failed"
    exit 1
fi
