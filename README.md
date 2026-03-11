# llm-gateway

LLM API proxy with semantic caching, cost control, and observability — unified proxy to OpenAI and Anthropic with Redis cache, per-tenant rate limiting, model fallback, and PostgreSQL audit/usage dashboard.

## Structure

```
llm-gateway/
├── app/
│   ├── main.py              # FastAPI app
│   ├── proxy.py             # Core proxy logic + provider routing
│   ├── providers/
│   │   ├── openai_provider.py
│   │   └── anthropic_provider.py
│   ├── cache/
│   │   ├── semantic_cache.py
│   │   └── redis_client.py
│   ├── security/
│   │   ├── injection_scanner.py
│   │   ├── permissions.py
│   │   └── prompt_isolation.py
│   ├── observability/
│   │   ├── audit_logger.py
│   │   ├── usage_tracker.py
│   │   └── dashboard.py
│   ├── rate_limiter.py
│   ├── fallback.py
│   ├── schemas.py
│   └── db.py
├── db/
│   └── init.sql
├── tests/
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md
```

## How to run

1. Copy `.env.example` to `.env` and set `OPENAI_API_KEY` (and optionally `ANTHROPIC_API_KEY`).
2. Start dependencies and app:
   ```bash
   docker-compose up -d postgres redis
   # Create DB and run init.sql if needed, then:
   docker-compose up --build app
   ```
   Or run everything: `docker-compose up --build`
3. API: http://localhost:8000  
   - Docs: http://localhost:8000/docs  
   - Chat: `POST /v1/chat/completions` (OpenAI-compatible body; use header `X-Tenant-ID` for tenant).  
   - Dashboard: `GET /dashboard/usage`, `/dashboard/latency`, `/dashboard/cache`, `/dashboard/errors`

## API documentation

Swagger UI: http://localhost:8000/docs
