#!/bin/bash
# Automated test runner for Multi-Chain Technical Risk Scoring System

echo "🧪 Running Multi-Chain Technical Risk Scoring System Tests"
echo "=========================================================="

# Activate virtual environment
source venv/bin/activate

# Run configuration test
echo ""
echo "📋 Testing Configuration..."
python3 config.py
if [ $? -ne 0 ]; then
    echo "❌ Configuration test failed"
    exit 1
fi

# Run Ethereum adapter tests
echo ""
echo "🔷 Testing Ethereum Adapter..."
pytest tests/test_ethereum.py -v
if [ $? -ne 0 ]; then
    echo "❌ Ethereum tests failed"
    exit 1
fi

# Run Hedera adapter tests
echo ""
echo "🔶 Testing Hedera Adapter..."
pytest tests/test_hedera.py -v
if [ $? -ne 0 ]; then
    echo "❌ Hedera tests failed"
    exit 1
fi

# Run integration tests
echo ""
echo "🔗 Testing Integration Pipeline..."
pytest tests/test_integration.py -v
if [ $? -ne 0 ]; then
    echo "❌ Integration tests failed"
    exit 1
fi

echo ""
echo "=========================================================="
echo "✅ All tests passed successfully!"
echo ""
