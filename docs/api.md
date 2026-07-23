# API Design

All endpoints are versioned under `/api/v1`.

## Endpoints

| Method | Path | Purpose | Auth Required | Admin Only |
|--------|------|---------|---------------|------------|
| GET | `/health` | Service and dependency health | No | No |
| POST | `/auth/register` | Create an account (email, full_name, password) | No | No |
| POST | `/auth/login` | Issue JWT access token | No | No |
| GET | `/auth/me` | Current authenticated user profile | Yes | No |
| POST | `/chat/query` | Citation-grounded legal answer | Yes | No |
| POST | `/chat/stream` | Server-sent event streaming answer | Yes | No |
| GET | `/chat/history` | User chat history (last 50) | Yes | No |
| POST | `/search/legal` | Search Indian Kanoon legal database | Yes | No |
| GET | `/documents/{document_id}` | Fetch normalized Indian Kanoon document | Yes | No |
| POST | `/documents/index` | Index document chunks into ChromaDB | Yes | No |
| POST | `/feedback` | Record user feedback (rating 1-5) | Yes | No |
| GET | `/evaluation/results` | Evaluation benchmark results | Yes | No |
| POST | `/evaluation/run` | Run or seed benchmark evaluation | Yes | Yes |
| GET | `/admin/metrics` | Operational metrics (chats, refusals, cache hits, etc.) | Yes | Yes |
| GET | `/admin/guardrails` | Guardrail audit log entries | Yes | Yes |
| GET | `/metrics` | Prometheus-style metrics snapshot | No | No |

## Authentication

Use JWT Bearer tokens:

```bash
# Login
curl -X POST /api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"yourpassword"}'

# Response: {"access_token": "eyJ...", "token_type": "bearer"}

# Use the token for authenticated requests
curl -X POST /api/v1/chat/query \
  -H "Authorization: Bearer eyJ..." \
  -H "Content-Type: application/json" \
  -d '{"query":"What is anticipatory bail?"}'
```

## Error Format

All errors use a structured JSON payload:

```json
{
  "detail": "Human-readable error message"
}
```

Validation errors (422) include field-level details:

```json
{
  "detail": [
    {
      "loc": ["body", "query"],
      "msg": "String should have at least 3 characters",
      "type": "string_too_short"
    }
  ]
}
```

HTTP status codes used:
- `200` — Success
- `201` — Created (registration)
- `401` — Unauthorized (missing or expired token)
- `403` — Forbidden (non-admin accessing admin endpoint)
- `404` — Not found
- `409` — Conflict (duplicate email on register)
- `422` — Validation error
- `500` — Internal server error
