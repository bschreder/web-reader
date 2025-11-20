#!/usr/bin/env bash
# Test runner script for all services
# Usage: ./scripts/test-all.sh [unit|integration|e2e|all] [--fail-on-error]

set -e

TEST_TYPE="${1:-unit}"
FAIL_ON_ERROR=false

# Parse arguments
for arg in "$@"; do
    case $arg in
        --fail-on-error)
            FAIL_ON_ERROR=true
            shift
            ;;
        unit|integration|e2e|all)
            TEST_TYPE="$arg"
            shift
            ;;
    esac
done

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "========================================="
echo "Web Reader - Test Runner"
echo "========================================="
echo "Test Type: $TEST_TYPE"
echo "Fail on Error: $FAIL_ON_ERROR"
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
        if [ "$FAIL_ON_ERROR" = true ]; then
            pytest tests/unit --cov=src --cov-branch --cov-report=term-missing --cov-fail-under=80
        else
            pytest tests/unit --cov=src --cov-branch --cov-report=term-missing --cov-fail-under=80 || echo "  ⚠ Tests failed or coverage below 80%"
        fi
    fi
    
    if [ "$TEST_TYPE" = "integration" ] || [ "$TEST_TYPE" = "all" ]; then
        echo "  → Integration tests"
        if [ "$FAIL_ON_ERROR" = true ]; then
            pytest tests/integration -v
        else
            pytest tests/integration -v || echo "  ⚠ Integration tests failed"
        fi
    fi
    
    if [ "$TEST_TYPE" = "e2e" ] || [ "$TEST_TYPE" = "all" ]; then
        echo "  → E2E tests"
        if [ "$FAIL_ON_ERROR" = true ]; then
            pytest tests/e2e -v
        else
            pytest tests/e2e -v || echo "  ⚠ E2E tests failed"
        fi
    fi
}

run_frontend_tests() {
    echo ""
    echo ">>> Running frontend tests"
    cd "$PROJECT_ROOT/frontend"
    
    if [ "$TEST_TYPE" = "unit" ] || [ "$TEST_TYPE" = "all" ]; then
        echo "  → Unit tests"
        if [ "$FAIL_ON_ERROR" = true ]; then
            npm run test:unit
        else
            npm run test:unit || echo "  ⚠ Unit tests failed"
        fi
    fi
    
    if [ "$TEST_TYPE" = "integration" ] || [ "$TEST_TYPE" = "all" ]; then
        echo "  → Browser tests"
        if [ "$FAIL_ON_ERROR" = true ]; then
            npm run test:browser
        else
            npm run test:browser || echo "  ⚠ Browser tests failed"
        fi
    fi
    
    if [ "$TEST_TYPE" = "e2e" ] || [ "$TEST_TYPE" = "all" ]; then
        echo "  → E2E tests"
        if [ "$FAIL_ON_ERROR" = true ]; then
            npx playwright test tests/e2e
        else
            npx playwright test tests/e2e || echo "  ⚠ E2E tests failed"
        fi
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
