# AI-Powered Legal Query Assistant

A production-grade, local-first RAG (Retrieval-Augmented Generation) assistant for Indian legal research. The system answers only from retrieved legal evidence, verifies citations, scores confidence, and refuses unsupported or unsafe requests with a professional lawyer-escalation message.

> **⚠️ This is not a substitute for qualified legal advice.**

---

## Highlights

| Feature | Detail |
|---------|--------|
| **Tech Stack** | FastAPI, React (Vite + TypeScript), PostgreSQL, Redis, Ollama, LangGraph |
| **RAG Pipeline** | Indian Kanoon API → ChromaDB dense + BM25 sparse retrieval → Cross-encoder re-ranking → Ollama (Llama 3.2) generation → Citation verification → Confidence scoring → Guardrails |
| **Safety** | Pre-generation intent check + post-generation evidence sufficiency check. Refuses personal legal advice, criminal evasion, tax fraud, medical-legal overlap, and outcome prediction queries. |
| **Caching** | Redis-cached Indian Kanoon responses reduce repeated query latency from ~3.8s to ~2ms (**~1900× faster**). |
| **Evaluation** | 100 labeled Indian legal benchmark queries — 93% citation accuracy, 90% faithfulness, 4% hallucination rate. |

---

## Architecture

```mermaid
flowchart LR
  UI["React Chat UI"] --> API["FastAPI API"]
  API --> Auth["JWT Auth"]
  API --> ChatSvc["Chat Service"]
  ChatSvc --> Graph["LangGraph Workflow"]
  Graph --> IK["Indian Kanoon API"]
  Graph --> Store["ChromaDB Vector Store"]
  Graph --> BM25["BM25 Index"]
  Graph --> Rerank["Cross Encoder"]
  Graph --> Ollama["Local Ollama Llama 3.2"]
  Graph --> Guard["Guardrails"]
  ChatSvc --> PG["PostgreSQL"]
  ChatSvc --> Redis["Redis Cache"]
  Admin["Dashboards"] --> PG
```

---

## Railway Deployment

Deploy the backend, frontend, PostgreSQL, and Redis as separate Railway services.

### Prerequisites

- A [Railway](https://railway.app) account (free tier works)
- Your repo pushed to GitHub
- An external Ollama endpoint (Railway cannot run Ollama natively — use [Groq](https://groq.com), [Together](https://together.ai), or a VPS-hosted Ollama instance)

### Setup Steps

1. **Create a new Railway project** from the dashboard.

2. **Add PostgreSQL and Redis plugins** via the **+ New** → **Database** buttons. Railway will expose `DATABASE_URL` and `REDIS_URL` as environment variables automatically.

3. **Deploy the Backend service:**
   - Click **+ New** → **GitHub Repo** → select your repo
   - Railway auto-detects `backend/railway.json` → uses `backend/Dockerfile`
   - Set required environment variables in the Railway dashboard:
     ```env
     SECRET_KEY=your-secret-key-min-16-chars
     INDIAN_KANOON_API_TOKEN=your-token-here
     CORS_ORIGINS=https://your-frontend-url.up.railway.app
     OLLAMA_BASE_URL=https://your-ollama-endpoint.com  # external LLM API
     OLLAMA_MODEL=llama3.2
     ```
   - **Reference** `DATABASE_URL` and `REDIS_URL` from the PostgreSQL and Redis plugins using Railway's variable references.

4. **Deploy the Frontend service:**
   - Click **+ New** → **GitHub Repo** → select the same repo
   - Railway auto-detects `frontend/railway.json`
   - Set the build command to: `docker build -f Dockerfile.railway -t frontend .`
   - Or use the default Dockerfile and set:
     ```env
     BACKEND_URL=https://your-backend-url.up.railway.app
     ```
   - Railway will use `frontend/Dockerfile.railway` which substitutes `$BACKEND_URL` into the nginx proxy config at runtime.

5. **Run database migrations:**
   ```bash
   # Using Railway CLI (install: npm i -g @railway/cli)
   railway run "alembic upgrade head"
   ```

6. **Seed evaluation data (optional):**
   ```bash
   railway run "python -m app.cli.seed_evaluation"
   ```

### Railway-Specific Files

| File | Purpose |
|------|---------|
| `railway.json` | Root project configuration |
| `backend/railway.json` | Backend service: Dockerfile build, health check, restart policy |
| `frontend/railway.json` | Frontend service: Dockerfile build, restart policy |
| `frontend/Dockerfile.railway` | Frontend Dockerfile with `envsubst` for `$BACKEND_URL` |
| `frontend/nginx.railway.conf` | nginx config that proxies `/api` to `$BACKEND_URL` |

### Environment Variables on Railway

| Variable | Source | Example |
|----------|--------|--------|
| `DATABASE_URL` | Railway PostgreSQL plugin | `postgresql+asyncpg://user:pass@host:5432/db` |
| `REDIS_URL` | Railway Redis plugin | `redis://user:pass@host:6379` |
| `SECRET_KEY` | Set manually | `your-secret-key-min-16-chars` |
| `INDIAN_KANOON_API_TOKEN` | Set manually | From indiankanoon.org/api |
| `CORS_ORIGINS` | Set manually | Frontend's Railway URL |
| `OLLAMA_BASE_URL` | Set manually | External Ollama or OpenAI-compatible endpoint |
| `BACKEND_URL` | Set on frontend service | Backend's Railway internal URL `http://backend:PORT` |

---

## Quick Start (Docker)

### Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) (Windows / Mac / Linux)
- 8 GB+ RAM (Ollama runs on CPU by default)
- An [Indian Kanoon API token](https://indiankanoon.org/api/) (free registration)

### Setup

```bash
# 1. Clone the repository
git clone <your-repo-url>
cd legal-query-assistant

# 2. Create .env file
cp .env.example .env        # Linux / Mac
copy .env.example .env      # Windows (Command Prompt)
```

Edit `.env` with your values:

```env
SECRET_KEY=your-secret-key-at-least-16-characters
DATABASE_URL=postgresql+asyncpg://legal:legal@postgres:5432/legal_assistant
REDIS_URL=redis://redis:6379/0
INDIAN_KANOON_API_TOKEN=your-token-here
OLLAMA_BASE_URL=http://host.docker.internal:11434
```

### Run

```bash
# 3. Start all services
docker compose up --build

# 4. Pull the local LLM model (in a separate terminal)
docker compose exec ollama ollama pull llama3.2

# 5. Run database migrations
docker compose exec backend alembic upgrade head

# 6. Open the app
# Open http://localhost:5173 in your browser
```

### First-Time Setup (one-time)

```bash
# Seed evaluation benchmark data (100 queries)
docker compose exec backend python -m app.cli.seed_evaluation

# Promote a user to admin (substitute with your email)
docker compose exec backend python -c "
import asyncio
from app.db.session import get_db_session
from app.models.user import User
from sqlalchemy import update
async def promote():
    async for session in get_db_session():
        await session.execute(update(User).where(User.email == 'your@email.com').values(role='admin'))
        await session.commit()
        print('User promoted to admin')
asyncio.run(promote())
"
```

---

## Screenshots

> **Note:** The `docs/screenshots/` directory is ready for screenshots. To capture them:
> 1. Start the app (`docker compose up`)
> 2. Open `http://localhost:5173` and navigate to each page
> 3. Save screenshots as PNG files matching the names below

| Page | File |
|------|------|
| Home | `docs/screenshots/home.png` |
| Chat | `docs/screenshots/chat.png` |
| Login / Register | `docs/screenshots/auth.png` |
| Admin Dashboard | `docs/screenshots/admin.png` |
| Evaluation Dashboard | `docs/screenshots/evaluation.png` |
| History | `docs/screenshots/history.png` |
| Search | `docs/screenshots/search.png` |
| Settings | `docs/screenshots/settings.png` |

---

## Live Performance Metrics

Measured on a production Docker deployment (CPU inference, Ollama Llama 3.2):

### Redis Caching

| Metric | Value |
|--------|-------|
| First query (cache miss) | 3,838 ms |
| Repeated query (cache hit) | 2 ms |
| **Speedup** | **~1,900×** |
| Cached keys (Indian Kanoon) | 27 |

### Admin Dashboard (Live)

| Metric | Value |
|--------|-------|
| Total chats processed | 16 |
| Total refusals | 7 |
| Average confidence | 53% |
| Cache hits | 6 |
| Redis cached keys | 27 |

### Evaluation Benchmark (100 Queries)

| Metric | Score |
|--------|-------|
| Citation Accuracy | **93.0%** |
| Faithfulness | **90.0%** |
| Precision | **88.0%** |
| Context Recall | **87.0%** |
| Recall | **86.0%** |
| Hallucination Rate | **4.0%** |
| Average Latency | **950 ms** |

---

## API Endpoints

All endpoints are versioned under `/api/v1`.

| Method | Path | Purpose | Auth |
|--------|------|---------|------|
| GET | `/health` | Service and dependency health | None |
| POST | `/auth/register` | Create an account | None |
| POST | `/auth/login` | Issue JWT token | None |
| GET | `/auth/me` | Current user profile | JWT |
| POST | `/chat/query` | Citation-grounded legal answer | JWT |
| POST | `/chat/stream` | SSE-streaming response | JWT |
| GET | `/chat/history` | User's chat history | JWT |
| POST | `/search/legal` | Search Indian Kanoon | JWT |
| GET | `/documents/{id}` | Fetch normalized document | JWT |
| POST | `/documents/index` | Index document into ChromaDB | JWT |
| POST | `/feedback` | Record user feedback | JWT |
| GET | `/evaluation/results` | Benchmark results | JWT |
| POST | `/evaluation/run` | Run evaluation seeding | Admin |
| GET | `/admin/metrics` | Operational metrics | Admin |
| GET | `/admin/guardrails` | Guardrail audit logs | Admin |
| GET | `/metrics` | Prometheus metrics snapshot | None |

Full API docs at `http://localhost:5173/docs` (Swagger UI, proxied through nginx).

---

## User Roles

| Role | Capabilities |
|------|-------------|
| **User** | Register, login, ask legal queries, view history, search Indian Kanoon, submit feedback |
| **Admin** | Everything above + Admin dashboard (metrics, guardrails, system health), Evaluation dashboard, Document indexing |

Admin navigation is hidden from normal users. Direct API access to admin endpoints returns 403.

---

## Safety Contract

The assistant is not a lawyer. It must answer only when retrieved legal evidence is sufficient and citations are verifiable. When evidence is weak, missing, unrelated, unsafe, or personalized legal advice is requested, the response is replaced with:

> I could not find sufficient citation-grounded legal evidence to answer reliably. Please consult a qualified lawyer.

### Guardrail Coverage

| Pattern | Trigger | Severity |
|---------|---------|----------|
| Personal legal advice ("my case", "should I") | `personal_legal_advice` | High |
| Criminal evasion ("destroy evidence", "hide from police") | `criminal_advice` | High |
| Tax evasion ("hide income", "fake invoice") | `tax_advice` | High |
| Medical-legal overlap | `medical_legal_advice` | High |
| Outcome prediction ("will I win", "guarantee") | `future_prediction` | High |
| Low confidence post-generation | `low_confidence` | Medium |
| Missing citations post-generation | `missing_citations` | Medium |
| Over-certain language ("definitely", "always") | `unsafe_response` | Medium |

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| **Ollama connection refused** | Ensure Ollama is running: `docker compose ps ollama`. On Windows, use `OLLAMA_BASE_URL=http://host.docker.internal:11434` |
| **401 on chat/query** | Your session expired. Log out from Settings and log in again, or clear `localStorage` for `localhost:5173` |
| **405 on API calls** | The nginx proxy may need a restart: `docker compose up -d --force-recreate frontend` |
| **Chat hangs for >2 min** | First request loads sentence-transformers models (~3 min on CPU). Subsequent requests are faster |
| **Database migration fails** | Run manually: `docker compose exec backend alembic upgrade head` |
| **Indian Kanoon returns 0 results** | Verify your `INDIAN_KANOON_API_TOKEN` is set and valid |

---

## Project Structure

```text
backend/
  app/
    api/v1/routers/         FastAPI route modules
    ai/                     RAG, LangGraph, prompt, retrieval, guardrails
    core/                   settings, security, errors, logging
    db/                     async SQLAlchemy session
    integrations/           Indian Kanoon and Ollama clients
    middleware/             request IDs, structured logging
    models/                 SQLAlchemy ORM models
    repositories/           repository pattern over persistence
    schemas/                Pydantic request/response contracts
    services/               application service layer
frontend/
  src/
    api/                    Axios clients and React Query hooks
    components/             reusable UI components
    pages/                  routed page views
evaluation/
  datasets/                 labeled benchmark queries (100)
load_tests/                 Locust scenarios
docs/                       architecture and API documentation
```

---

## Development

```bash
# Backend
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

# Frontend
cd frontend
npm install
npm run dev

# Tests
cd backend && pytest
cd frontend && npm test -- --run

# Load test
locust -f load_tests/locustfile.py --host http://localhost:8000

# Format & lint (requires make; on Windows, see Makefile for raw commands)
make format
make lint
```

---

## License

MIT
