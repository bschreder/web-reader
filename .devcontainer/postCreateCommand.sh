#!/usr/bin/env bash
set -e

# Ensure user-local bin is on PATH so uv-installed scripts are available
export PATH="$HOME/.local/bin:$PATH"

# Verify uv is available
if ! command -v uv >/dev/null 2>&1; then
  echo "Error: uv not found on PATH. Current PATH: $PATH"
  echo "Make sure the devcontainer image is rebuilt so uv is installed."
  exit 1
fi

# Install frontend dependencies
if [ -d "/workspaces/web-reader/apps/frontend" ]; then
  # Clean up stale contents and package-lock
  if [ -d "/workspaces/web-reader/apps/frontend/node_modules" ]; then
    find /workspaces/web-reader/apps/frontend/node_modules -mindepth 1 -delete 2>/dev/null || true
  fi
  rm -f /workspaces/web-reader/apps/frontend/package-lock.json
  npm cache clean --force 2>/dev/null || true
  
  # Install fresh dependencies
  npm --prefix /workspaces/web-reader/apps/frontend install --loglevel=warn --legacy-peer-deps
  npx --prefix /workspaces/web-reader/apps/frontend playwright install --with-deps chromium
fi

# Install Python dependencies for all services using uv
for svc in backend fastmcp langchain; do
  svcdir="/workspaces/web-reader/apps/$svc"
  if [ -d "$svcdir" ] && [ -f "$svcdir/pyproject.toml" ]; then
    echo "Installing Python dependencies for $svc via uv..."
    # Clean up any stale venv to avoid permission issues
    rm -rf "$svcdir/.venv" "$svcdir/__pycache__" "$svcdir/build" "$svcdir/dist"
    (cd "$svcdir"  && uv lock && uv sync --all-groups)
  fi
done

# Docker network bridge setup removed: compose now manages service networking.

echo "Devcontainer ready"
