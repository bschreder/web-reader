#!/usr/bin/env bash
set -e

# Install frontend dependencies
if [ -d "/workspaces/web-reader/frontend" ]; then
  (npm --prefix /workspaces/web-reader/frontend ci || npm --prefix /workspaces/web-reader/frontend install)
  npx --prefix /workspaces/web-reader/frontend playwright install chromium --with-deps || true
fi

# Install Python dependencies for all services
for svc in backend fastmcp langchain; do
  svcdir="/workspaces/web-reader/$svc"
  if [ -d "$svcdir" ]; then
    if [ -f "$svcdir/requirements-dev.txt" ]; then
      pip install -r "$svcdir/requirements-dev.txt"
    elif [ -f "$svcdir/requirements.txt" ]; then
      pip install -r "$svcdir/requirements.txt"
    fi
  fi
done

echo "Devcontainer ready"
