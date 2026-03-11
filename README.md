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

*(TODO: docker-compose up instructions.)*

## API documentation

*(TODO: Link to Swagger after implementation.)*
