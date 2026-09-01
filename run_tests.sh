#!/bin/bash
# WildGuard Kenya - Test Execution Script
# Runs all test suites and generates reports

set -e

echo "╔════════════════════════════════════════════════════════════╗"
echo "║     WildGuard Kenya - Test Suite Execution                ║"
echo "╚════════════════════════════════════════════════════════════╝"

cd "$(dirname "$0")"

if [ ! -d "backend" ]; then
    echo "❌ Error: backend directory not found"
    exit 1
fi

cd backend

# Activate virtual environment
if [ ! -d ".venv" ]; then
    echo "❌ Virtual environment not found. Run setup.sh first."
    exit 1
fi

source .venv/bin/activate

echo ""
echo "🧪 Running test suite..."
echo ""

# Run comprehensive test suite with pytest
echo "📋 Running comprehensive pytest tests..."
python -m pytest test_api_comprehensive.py -v --tb=short 2>&1 || PYTEST_FAILED=1

# Run Django tests
echo ""
echo "📋 Running Django test suite..."
python manage.py test --verbosity=2 2>&1 || DJANGO_TESTS_FAILED=1

# Run E2E tests if database is available
echo ""
echo "🚀 Running E2E tests..."
python run_e2e_tests.py 2>&1 || E2E_FAILED=1

# Summary
echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║                    Test Results Summary                    ║"
echo "╠════════════════════════════════════════════════════════════╣"

if [ -z "$PYTEST_FAILED" ]; then
    echo "✓ Pytest comprehensive tests: PASSED"
else
    echo "✗ Pytest comprehensive tests: FAILED"
fi

if [ -z "$DJANGO_TESTS_FAILED" ]; then
    echo "✓ Django test suite: PASSED"
else
    echo "✗ Django test suite: FAILED"
fi

if [ -z "$E2E_FAILED" ]; then
    echo "✓ E2E API tests: PASSED"
else
    echo "✗ E2E API tests: FAILED"
fi

echo "╚════════════════════════════════════════════════════════════╝"

# Generate coverage report
echo ""
echo "📊 Generating coverage report..."
coverage run --source='.' manage.py test --noinput 2>/dev/null || true
coverage report
coverage html

echo ""
echo "✓ Coverage report generated in htmlcov/index.html"

# Exit with failure if any tests failed
if [ -n "$PYTEST_FAILED" ] || [ -n "$DJANGO_TESTS_FAILED" ] || [ -n "$E2E_FAILED" ]; then
    echo ""
    echo "⚠️  Some tests failed. Please review the output above."
    exit 1
else
    echo ""
    echo "✅ All tests passed!"
    exit 0
fi
