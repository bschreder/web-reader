FROM python:3.13-slim AS base
WORKDIR /app
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    curl \
    ca-certificates && \
    rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

FROM base AS prod
COPY . .
RUN useradd -m -u 1000 fastmcp && chown -R fastmcp:fastmcp /app
USER fastmcp
EXPOSE 3000
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 CMD python3 -c "import sys; sys.exit(0)"
CMD ["python", "server.py"]

FROM base AS dev
COPY requirements-debug.txt ./
RUN pip install --no-cache-dir -r requirements-debug.txt
COPY . .
RUN useradd -m -u 1000 fastmcp && chown -R fastmcp:fastmcp /app
USER fastmcp
EXPOSE 3000 5673
# Support optional debugpy via DEBUGPY_PORT env var
CMD ["sh", "-c", "if [ -n \"$DEBUGPY_PORT\" ]; then python -m debugpy --listen 0.0.0.0:$DEBUGPY_PORT server.py; else watchfiles --ignore-paths '*.pyc,__pycache__' python server.py; fi"]
