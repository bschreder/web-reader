# Web Reader Release Guide

## Compose Profiles

- Base: `infra/compose/compose.yaml`
- Dev override: `infra/compose/compose.dev.yaml`
- Prod override: `infra/compose/compose.prod.yaml`

## Production Startup

1. Prepare environment:

```powershell
Copy-Item infra/env/.env.prod.example .env
```

2. Build and start production stack:

```powershell
docker compose -f infra/compose/compose.yaml -f infra/compose/compose.prod.yaml --env-file .env --profile infra --profile app up -d --build
```

3. Verify health:

```powershell
curl http://localhost:3101/health
curl http://localhost:8001/health
curl http://localhost:8000/health
```

4. Stop stack:

```powershell
docker compose -f infra/compose/compose.yaml -f infra/compose/compose.prod.yaml --env-file .env --profile infra --profile app down
```

## Image Tagging

Set these in `.env` for release builds:

- `IMAGE_TAG`
- `FRONTEND_IMAGE`
- `BACKEND_IMAGE`
- `LANGCHAIN_IMAGE`
- `FASTMCP_IMAGE`

Compose prod override reads those values and publishes deterministic image names.
