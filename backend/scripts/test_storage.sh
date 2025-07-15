#!/bin/bash
# Script to test storage functionality

echo "🧪 Running Storage Tests"
echo "======================="

# Get the poetry environment Python
PYTHON_BIN="/Users/duncanjurman/Library/Caches/pypoetry/virtualenvs/swallowtail-backend-lnUnKcVu-py3.12/bin/python"

# Change to backend directory
cd "$(dirname "$0")/.."

# Run tests
echo "Running complete storage test..."
$PYTHON_BIN tests/test_storage_complete.py

echo -e "\n✅ Storage tests completed!"