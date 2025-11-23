FROM python:3.13-slim AS base
WORKDIR /app
RUN apt-get update -y && apt-get install -y --no-install-recommends \
    build-essential curl pipx && \
    pipx ensurepath && \
    rm -rf /var/lib/apt/lists/*
ENV PATH="/root/.local/bin:${PATH}"
RUN pipx install poetry

COPY pyproject.toml poetry.lock* ./
# Configure Poetry to create a virtualenv inside the project at `.venv`
ENV POETRY_VIRTUALENVS_CREATE=true
ENV POETRY_VIRTUALENVS_IN_PROJECT=true
ENV PATH="/app/.venv/bin:${PATH}"
RUN poetry install --only main --no-root --no-interaction --no-ansi

FROM base AS prod
COPY . .
RUN useradd -m -u 1000 fastmcp && chown -R fastmcp:fastmcp /app
USER fastmcp
EXPOSE 3000
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 CMD python3 -c "import sys; sys.exit(0)"
CMD ["python", "server.py"]

FROM base AS dev
COPY pyproject.toml poetry.lock* ./
# Install development and debug dependencies so debugpy is available
RUN poetry install --with dev,debug --no-root --no-interaction --no-ansi
COPY . .
RUN useradd -m -u 1000 fastmcp && chown -R fastmcp:fastmcp /app
USER fastmcp
EXPOSE 3000 5673
# Support optional debugpy via DEBUGPY_PORT env var
CMD ["sh", "-c", "if [ -n \"$DEBUGPY_PORT\" ]; then python -m debugpy --listen 0.0.0.0:$DEBUGPY_PORT server.py; else watchfiles --ignore-paths '*.pyc,__pycache__' python server.py; fi"]
