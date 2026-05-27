# LangChain Orchestrator Dockerfile
FROM python:3.13-slim AS base
WORKDIR /app
RUN apt-get update -y && apt-get install -y --no-install-recommends \
    build-essential curl && \
    rm -rf /var/lib/apt/lists/*
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:${PATH}"

COPY pyproject.toml uv.lock* ./
COPY README.md ./
COPY src ./src
ENV PATH="/app/.venv/bin:${PATH}"
RUN uv lock && uv sync --no-dev

FROM base AS prod
COPY . .
EXPOSE 8001
CMD ["python", "server.py"]

FROM base AS dev
COPY pyproject.toml uv.lock* ./
RUN uv lock && uv sync --all-groups
COPY . .
EXPOSE 8001 5672
# Support optional debugpy via DEBUGPY_PORT env var
CMD ["sh", "-c", "if [ -n \"$DEBUGPY_PORT\" ]; then python -m debugpy --listen 0.0.0.0:$DEBUGPY_PORT server.py; else watchfiles --ignore-paths '*.pyc,__pycache__' python server.py; fi"]
