#!/usr/bin/env bash
# Open VS Code Testing UI - Quick Start

echo "========================================="
echo "VS Code Testing UI - Quick Start"
echo "========================================="
echo ""
echo "Setting up interactive testing in VS Code..."
echo ""

# Check if running in VS Code terminal
if [ -z "$TERM_PROGRAM" ] || [ "$TERM_PROGRAM" != "vscode" ]; then
    echo "⚠️  This script is designed to run in VS Code's integrated terminal"
    echo "   Please open this workspace in VS Code first"
    echo ""
fi

# Check if multi-root workspace file exists
if [ -f "web-reader.code-workspace" ]; then
    echo "✅ Multi-root workspace found: web-reader.code-workspace"
    echo ""
    echo "📂 Workspace contains:"
    echo "   • FastMCP (Python tests)"
    echo "   • Backend (Python tests)"
    echo "   • LangChain (Python tests)"
    echo "   • Frontend (Vitest tests)"
    echo ""
else
    echo "❌ Workspace file not found"
    exit 1
fi

# Check for test files
echo "🔍 Checking test discovery..."
echo ""

for project in fastmcp backend langchain; do
    if [ -d "$project/tests" ]; then
        test_count=$(find "$project/tests" -name "test_*.py" | wc -l)
        echo "   $project: $test_count test files"
    fi
done

if [ -d "frontend/tests" ]; then
    test_count=$(find "frontend/tests" -name "*.test.*" -o -name "*.spec.*" | wc -l)
    echo "   frontend: $test_count test files"
fi

echo ""
echo "========================================="
echo "🎯 How to Use Testing UI:"
echo "========================================="
echo ""
echo "1. Open Test Explorer:"
echo "   • Press: Ctrl+Shift+T (or Cmd+Shift+T on Mac)"
echo "   • Or click the 🧪 beaker icon in the Activity Bar"
echo ""
echo "2. Run tests interactively:"
echo "   • Click ▶️ next to any test to run it"
echo "   • Right-click → 'Debug Test' to debug with breakpoints"
echo "   • Use filters to show only failed/passed tests"
echo ""
echo "3. Multi-root workspace (recommended):"
echo "   • File → Open Workspace → select 'web-reader.code-workspace'"
echo "   • This shows all projects in one view"
echo ""
echo "📖 Full guide: README.VSCODE-TESTING.md"
echo ""
echo "========================================="
echo "✨ Setup Complete!"
echo "========================================="
