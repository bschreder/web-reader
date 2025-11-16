# Backend API Dockerfile
FROM python:3.13-slim AS base
WORKDIR /app
RUN apt-get update -y && apt-get install -y --no-install-recommends \
    build-essential curl && \
    rm -rf /var/lib/apt/lists/*
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

FROM base AS prod
COPY . .
EXPOSE 8000
CMD ["python", "server.py"]

# Dev stage with debug & reload support
FROM base AS dev
COPY requirements-debug.txt ./
RUN pip install --no-cache-dir -r requirements-debug.txt
COPY . .
EXPOSE 8000 5671
# Support optional debugpy via DEBUGPY_PORT env var
CMD ["sh", "-c", "if [ -n \"$DEBUGPY_PORT\" ]; then python -m debugpy --listen 0.0.0.0:$DEBUGPY_PORT -m uvicorn server:app --host 0.0.0.0 --port 8000 --reload; else uvicorn server:app --host 0.0.0.0 --port 8000 --reload; fi"]
