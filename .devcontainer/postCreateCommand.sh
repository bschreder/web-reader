#!/usr/bin/env bash
set -e

# Ensure user-local bin is on PATH so pipx/poetry-installed scripts are available
export PATH="$HOME/.local/bin:$PATH"

# Verify poetry is available
if ! command -v poetry >/dev/null 2>&1; then
  echo "Error: poetry not found on PATH. Current PATH: $PATH"
  echo "Make sure the devcontainer image is rebuilt so Poetry is installed."
  exit 1
fi

# Install frontend dependencies
if [ -d "/workspaces/web-reader/frontend" ]; then
  # Clean up stale contents and package-lock
  if [ -d "/workspaces/web-reader/frontend/node_modules" ]; then
    find /workspaces/web-reader/frontend/node_modules -mindepth 1 -delete 2>/dev/null || true
  fi
  rm -f /workspaces/web-reader/frontend/package-lock.json
  npm cache clean --force 2>/dev/null || true
  
  # Install fresh dependencies
  npm --prefix /workspaces/web-reader/frontend install --loglevel=warn
  npx --prefix /workspaces/web-reader/frontend playwright install chromium --with-deps || true
fi

# Install Python dependencies for all services using Poetry
for svc in backend fastmcp langchain; do
  svcdir="/workspaces/web-reader/$svc"
  if [ -d "$svcdir" ] && [ -f "$svcdir/pyproject.toml" ]; then
    echo "Installing Python dependencies for $svc via Poetry..."
    # Clean up any stale venv to avoid permission issues
    rm -rf "$svcdir/.venv" "$svcdir/__pycache__" "$svcdir/build" "$svcdir/dist"
    (cd "$svcdir"  && poetry lock --no-interaction --no-ansi && poetry install --with test,debug --no-interaction --no-ansi)
  fi
done

# Connect devcontainer to Docker networks for E2E testing
# This allows tests running in devcontainer to access service containers.
# Ensure external network exists and then attach this container.
EXTERNAL_NETWORK="external-services-network"
INTERNAL_NETWORK="web-reader-network"

echo "Ensuring Docker networks are available..."

# Create the external network if it doesn't already exist. This avoids race
# conditions when the devcontainer starts before ./start.ps1 provisions infra.
if ! docker network inspect "$EXTERNAL_NETWORK" >/dev/null 2>&1; then
  echo "Creating external network '$EXTERNAL_NETWORK'..."
  if ! docker network create "$EXTERNAL_NETWORK" >/dev/null 2>&1; then
    echo "Warning: Unable to create network '$EXTERNAL_NETWORK'."
  else
    echo "Created network '$EXTERNAL_NETWORK'."
  fi
else
  echo "Network '$EXTERNAL_NETWORK' already exists."
fi

# Prefer using the container ID as seen by the Docker daemon. `hostname`
# is commonly the container name but may not be resolvable by the Docker CLI
# depending on how the container was created; try to find a matching container
# entry first.
CONTAINER_NAME="$(hostname)"
CONTAINER_ID="$(docker ps --filter "id=${CONTAINER_NAME}" --format "{{.ID}}" 2>/dev/null || true)"

if [ -z "$CONTAINER_ID" ]; then
  CONTAINER_ID="$(docker ps --filter "name=${CONTAINER_NAME}" --format "{{.ID}}" 2>/dev/null || true)"
fi

if [ -z "$CONTAINER_ID" ]; then
  echo "Could not find a container matching '${CONTAINER_NAME}' via 'docker ps'."
  echo "Skipping automatic network connect — you can connect manually if needed."
else
  echo "Connecting devcontainer to Docker networks for E2E testing..."
  if docker network inspect "$INTERNAL_NETWORK" >/dev/null 2>&1; then
    docker network connect "$INTERNAL_NETWORK" "$CONTAINER_ID" 2>/dev/null || echo "Already connected to $INTERNAL_NETWORK"
  else
    echo "Network '$INTERNAL_NETWORK' not found; skipping connection."
  fi
  docker network connect "$EXTERNAL_NETWORK" "$CONTAINER_ID" 2>/dev/null || echo "Already connected to $EXTERNAL_NETWORK"
  echo "Network connections established"
fi

echo "Devcontainer ready"
