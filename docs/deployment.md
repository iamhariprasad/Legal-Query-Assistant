# Deployment Guide

## Local Production Run (Docker)

### Prerequisites

- Docker Desktop (Windows / Mac / Linux)
- 8 GB+ RAM recommended
- Ollama will run in its own container (CPU-only by default)
- Indian Kanoon API token (free registration at https://indiankanoon.org/api/)

### Steps

```bash
# 1. Copy environment configuration
copy .env.example .env   # Windows
# or
cp .env.example .env     # Linux / Mac

# 2. Edit .env with your values
# Required: SECRET_KEY, INDIAN_KANOON_API_TOKEN
# On Windows, use: OLLAMA_BASE_URL=http://host.docker.internal:11434

# 3. Start all services
docker compose up --build

# 4. In another terminal, pull the LLM model
docker compose exec ollama ollama pull llama3.2

# 5. Run database migrations
docker compose exec backend alembic upgrade head

# 6. (Optional) Seed evaluation benchmark data
docker compose exec backend python -m app.cli.seed_evaluation

# 7. Open the application
# http://localhost:5173
```

## Required Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `SECRET_KEY` | JWT signing key (min 16 chars) | `your-secret-key-at-least-16-characters` |
| `DATABASE_URL` | PostgreSQL async connection | `postgresql+asyncpg://legal:legal@postgres:5432/legal_assistant` |
| `REDIS_URL` | Redis connection | `redis://redis:6379/0` |
| `INDIAN_KANOON_API_TOKEN` | Indian Kanoon API token | Get from https://indiankanoon.org/api/ |
| `OLLAMA_BASE_URL` | Ollama API endpoint | `http://host.docker.internal:11434` (Windows) or `http://ollama:11434` (Linux) |

## Useful Docker Commands

```bash
# View all running services
docker compose ps

# Follow logs for all services
docker compose logs -f

# Follow logs for a specific service
docker compose logs -f backend
docker compose logs -f frontend
docker compose logs -f ollama

# Rebuild a single service after code changes
docker compose build backend
docker compose up -d --force-recreate backend

# Rebuild the frontend
docker compose build frontend
docker compose up -d --force-recreate frontend

# Run database migrations
docker compose exec backend alembic upgrade head

# Open a shell inside the backend container
docker compose exec backend bash

# Check Redis keys
docker compose exec redis redis-cli KEYS "ik:*"

# Check database row counts
docker compose exec backend python -c "
import asyncio
from app.db.session import get_db_session
from app.models.chat import ChatHistory
from app.models.evaluation import EvaluationResult
from app.models.search import SearchLog
from sqlalchemy import select, func
async def check():
    async for session in get_db_session():
        for table, label in [(ChatHistory,'Chats'),(SearchLog,'Search Logs'),(EvaluationResult,'Evaluations')]:
            count = (await session.execute(select(func.count()).select_from(table))).scalar()
            print(f'{label}: {count}')
asyncio.run(check())
"

# Stop all services
docker compose down
```

## Troubleshooting

### API returns 405
The nginx proxy may not have been rebuilt. Run:
```bash
docker compose build frontend
docker compose up -d --force-recreate frontend
```

### Chat query returns 401
Your session token has expired. Log out from the Settings page and log in again, or clear `localStorage` for `localhost:5173`.

### First query takes >2 minutes
The first RAG query downloads Sentence Transformer models (~90 MB). Wait for it to complete. Subsequent queries will be faster once the models are cached.

### "Could not find sufficient citation-grounded legal evidence"
This is expected for queries outside the assistant's evidence scope. The guardrails are functioning correctly.

### Redis connection refused
Ensure the Redis service is running: `docker compose ps redis`. If it restarted, the backend will reconnect automatically.

### Ollama returns connection refused
On Windows, ensure `OLLAMA_BASE_URL=http://host.docker.internal:11434` is set in `.env`. On Linux, the default `http://ollama:11434` works via Docker internal networking.

## Release Checklist

1. Run `docker compose build` to verify all images build cleanly
2. Run `docker compose up` and verify all services start without errors
3. Apply Alembic migrations: `docker compose exec backend alembic upgrade head`
4. Verify health endpoint returns 200: `curl http://localhost:5173/api/v1/health`
5. Pull the configured Ollama model: `docker compose exec ollama ollama pull llama3.2`
6. Register a test user and verify chat works end-to-end
7. Run evaluation seeding: `docker compose exec backend python -m app.cli.seed_evaluation`
8. Verify Admin dashboard loads with real metrics
9. Run Locust smoke test: `locust -f load_tests/locustfile.py --host http://localhost:8000`
