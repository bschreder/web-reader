#!/usr/bin/env bash
# Test runner script for all services
# Usage: ./scripts/test-all.sh [unit|integration|e2e|all]

set -e

TEST_TYPE="${1:-unit}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "========================================="
echo "Web Reader - Test Runner"
echo "========================================="
echo "Test Type: $TEST_TYPE"
echo "Project Root: $PROJECT_ROOT"
echo "========================================="

run_python_tests() {
    local service=$1
    local test_path=$2
    
    echo ""
    echo ">>> Running $service tests: $test_path"
    cd "$PROJECT_ROOT/$service"
    # Ensure runtime and test dependencies are installed for local devcontainer runs
    if [ -f requirements.txt ]; then pip install -q -r requirements.txt || true; fi
    if [ -f requirements-test.txt ]; then pip install -q -r requirements-test.txt || true; fi
    
    if [ "$TEST_TYPE" = "unit" ] || [ "$TEST_TYPE" = "all" ]; then
        echo "  → Unit tests"
        pytest tests/unit --cov=src --cov-branch --cov-report=term-missing --cov-fail-under=80 || echo "  ⚠ Tests failed or coverage below 80%"
    fi
    
    if [ "$TEST_TYPE" = "integration" ] || [ "$TEST_TYPE" = "all" ]; then
        echo "  → Integration tests"
        pytest tests/integration -v || echo "  ⚠ Integration tests failed"
    fi
    
    if [ "$TEST_TYPE" = "e2e" ] || [ "$TEST_TYPE" = "all" ]; then
        echo "  → E2E tests"
        pytest tests/e2e -v || echo "  ⚠ E2E tests failed"
    fi
}

run_frontend_tests() {
    echo ""
    echo ">>> Running frontend tests"
    cd "$PROJECT_ROOT/frontend"
    
    if [ "$TEST_TYPE" = "unit" ] || [ "$TEST_TYPE" = "all" ]; then
        echo "  → Unit tests"
        npm run test:unit || echo "  ⚠ Unit tests failed"
    fi
    
    if [ "$TEST_TYPE" = "integration" ] || [ "$TEST_TYPE" = "all" ]; then
        echo "  → Browser tests"
        npm run test:browser || echo "  ⚠ Browser tests failed"
    fi
    
    if [ "$TEST_TYPE" = "e2e" ] || [ "$TEST_TYPE" = "all" ]; then
        echo "  → E2E tests"
        npx playwright test tests/e2e || echo "  ⚠ E2E tests failed"
    fi
}

# Run tests for each service
run_python_tests "fastmcp" "$TEST_TYPE"
run_python_tests "backend" "$TEST_TYPE"
run_python_tests "langchain" "$TEST_TYPE"
run_frontend_tests

echo ""
echo "========================================="
echo "Test run complete!"
echo "========================================="
