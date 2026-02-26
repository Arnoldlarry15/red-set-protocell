#!/usr/bin/env bash

# Local CI-style validation script for Red Set ProtoCell
# Runs formatting, linting, and tests with fail-fast behavior

set -e  # Stop immediately on first failure

# Change to backend directory
cd "$(dirname "$0")/backend"

echo "================================"
echo "Running Black (code formatter)..."
echo "================================"
python -m black app/ tests/ --line-length 127

echo ""
echo "================================"
echo "Running isort (import sorter)..."
echo "================================"
python -m isort app/ tests/ --profile black --line-length 127

echo ""
echo "================================"
echo "Running flake8 (linter)..."
echo "================================"
# First check for critical errors (syntax errors, undefined names)
python -m flake8 app/ tests/ --count --select=E9,F63,F7,F82 --show-source --statistics
# Then check for style issues
python -m flake8 app/ tests/ --count --max-complexity=10 --max-line-length=127 --statistics

echo ""
echo "================================"
echo "Running pytest (tests)..."
echo "================================"
python -m pytest --maxfail=1 --disable-warnings -q

echo ""
echo "================================"
echo "✅ All checks passed!"
echo "================================"
