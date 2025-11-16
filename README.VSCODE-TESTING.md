# VS Code Testing UI Setup Guide

This workspace is configured for interactive testing using VS Code's native Testing UI.

## Quick Start

### 1. Open the Testing View

- **Keyboard**: `Ctrl+Shift+T` (Windows/Linux) or `Cmd+Shift+T` (Mac)
- **UI**: Click the beaker/flask icon 🧪 in the Activity Bar (left sidebar)
- **Command Palette**: `Ctrl+Shift+P` → "Test: Focus on Test Explorer View"

### 2. Using Multi-Root Workspace (Recommended)

For the best experience, open the multi-root workspace:

```bash
code web-reader.code-workspace
```

This shows all projects (FastMCP, Backend, LangChain, Frontend) in a single view with separate test explorers for each.

## Features

### Python Tests (FastMCP, Backend, LangChain)

The Testing UI will automatically discover pytest tests in:

- `tests/unit/`
- `tests/integration/`
- `tests/e2e/`

**Available Actions:**

- ▶️ **Run Test** - Click play icon next to any test/class/file
- 🐛 **Debug Test** - Right-click → "Debug Test" (sets breakpoints!)
- 🔄 **Rerun Failed** - Only run tests that failed
- 📊 **View Coverage** - See coverage inline in editor
- 🔍 **Go to Test** - Click test name to jump to code

**Test Markers:**

- 🟢 Passing test
- 🔴 Failed test
- ⏭️ Skipped test
- ⏱️ Slow test

### Frontend Tests (Vitest)

The Vitest extension provides interactive testing for:

- Unit tests (`tests/unit/`)
- Browser tests (`tests/browser/`)

**Available Actions:**

- ▶️ **Run/Debug tests** inline in editor (CodeLens)
- 📸 **Watch mode** - Auto-rerun on file save
- 🔍 **Filter tests** by name/file
- 📊 **Coverage view** with inline gutters

## Configuration

### Per-Project Python Settings

Each Python project (FastMCP, Backend, LangChain) has its own test discovery:

```json
{
  "python.testing.pytestEnabled": true,
  "python.testing.pytestArgs": ["tests"],
  "python.testing.cwd": "${workspaceFolder}"
}
```

### Frontend Vitest Settings

Frontend uses Vitest with projects for different test types:

```json
{
  "vitest.enable": true,
  "vitest.commandLine": "npm test --"
}
```

## Workflows

### Running Tests Interactively

1. **Single Test**: Click ▶️ next to test function
2. **Test File**: Click ▶️ next to filename
3. **Test Suite**: Click ▶️ next to folder or class
4. **All Tests**: Click ▶️ at workspace root

### Debugging Tests

1. Right-click any test → "Debug Test"
2. Set breakpoints in test or source code
3. Use Debug Console to inspect variables
4. Step through with F10 (over) / F11 (into)

### Filtering Tests

Use the Test Explorer filter box:

- Type test name: `test_navigation`
- By marker: `@integration`
- By status: Show only failed/passed/skipped

### Continuous Testing

**Python (pytest-watch):**

```bash
cd fastmcp
ptw tests/unit  # Reruns tests on file save
```

**Frontend (Vitest watch):**

```bash
cd frontend
npm test  # Vitest watch mode (auto-reruns)
```

Or use VS Code's "Enable Continuous Run" in Test Explorer.

## Test Organization

### Python Projects Structure

```
<service>/
├── tests/
│   ├── unit/           # Fast, isolated tests
│   │   ├── conftest.py
│   │   └── test_*.py
│   ├── integration/    # Tests with real services
│   │   ├── conftest.py
│   │   └── test_*.py
│   └── e2e/            # Full workflow tests
│       ├── conftest.py
│       └── test_*.py
├── pytest.ini
└── src/
```

### Frontend Structure

```
frontend/
├── tests/
│   ├── unit/           # Vitest unit tests (Node env)
│   ├── browser/        # Vitest browser tests (real browser)
│   └── e2e/            # Playwright E2E tests
├── vitest.config.ts
└── src/
```

## Keyboard Shortcuts

| Action               | Shortcut        |
| -------------------- | --------------- |
| Show Test Explorer   | `Ctrl+Shift+T`  |
| Run Test at Cursor   | `Ctrl+; Ctrl+R` |
| Debug Test at Cursor | `Ctrl+; Ctrl+D` |
| Rerun Last Test      | `Ctrl+; L`      |
| Go to Test           | `Ctrl+; Ctrl+G` |

## Tips & Tricks

### 1. Run Only Changed Tests

VS Code tracks file changes and can run only affected tests:

- Check "Run Tests on File Save" in Test Explorer settings

### 2. Coverage Inline

After running tests with coverage:

```bash
cd fastmcp && pytest tests/unit --cov=src --cov-report=html
```

Install "Coverage Gutters" extension to see coverage inline:

- Green: covered lines
- Red: uncovered lines
- Yellow: partially covered branches

### 3. Test Output Panel

View test output in:

- **Test Results** panel (bottom)
- **Output** → "Python Test Log" / "Vitest"
- **Terminal** for full pytest output

### 4. Debugging Integration Tests

For integration tests that need services running:

1. Start infrastructure:

   ```bash
   cd container && docker compose up -d
   ```

2. Set breakpoint in test
3. Debug test normally
4. Playwright/browser remains running during debug session

### 5. Test Markers

Run specific test types from command palette:

- `Python: Run Tests` → Select marker
- Choose: `unit`, `integration`, `e2e`, `slow`

Or use pytest args in settings:

```json
"python.testing.pytestArgs": [
  "tests",
  "-m",
  "unit"
]
```

## Troubleshooting

### Tests Not Discovered

**Python:**

1. Check Python interpreter is selected (bottom-right status bar)
2. Reload test discovery: Command Palette → "Test: Refresh Tests"
3. Check `pytest.ini` exists in project root
4. Verify `sys.path` includes project root (see `conftest.py`)

**Frontend:**

1. Ensure Vitest extension is installed
2. Check `vitest.config.ts` exists
3. Run `npm install` in frontend directory
4. Restart VS Code

### Tests Fail in UI but Pass in Terminal

- Check working directory: Tests run from workspace folder
- Environment variables may differ
- Use "Python: Run Tests" output panel for details

### Integration Tests Hang

- Ensure required services are running (Playwright, etc.)
- Check `skip_if_no_playwright` fixture is working
- Tests auto-skip if services unavailable

### Coverage Not Showing

1. Run tests with coverage first:
   ```bash
   pytest tests/unit --cov=src --cov-report=html
   ```
2. Install "Coverage Gutters" extension
3. Click "Watch" in status bar
4. Coverage overlays appear in editor

## Related Documentation

- **Testing Guide**: `README.TEST.md`
- **Project Plan**: `.github/project-plan.md`
- **Requirements**: `.github/requirements.md`

---

**Last Updated**: November 15, 2025
