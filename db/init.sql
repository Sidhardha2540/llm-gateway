-- LLM Gateway: audit log, usage tracking, tenant config

-- Audit log: every LLM request
CREATE TABLE IF NOT EXISTS audit_log (
    id BIGSERIAL PRIMARY KEY,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    tenant_id VARCHAR(255) NOT NULL,
    user_id VARCHAR(255),
    provider VARCHAR(50) NOT NULL,
    model VARCHAR(100) NOT NULL,
    prompt_tokens INT NOT NULL,
    completion_tokens INT NOT NULL,
    total_tokens INT NOT NULL,
    latency_ms INT,
    cost_usd DECIMAL(12, 6),
    cache_hit BOOLEAN DEFAULT FALSE,
    error_message TEXT
);

CREATE INDEX IF NOT EXISTS idx_audit_tenant ON audit_log(tenant_id);
CREATE INDEX IF NOT EXISTS idx_audit_created ON audit_log(created_at);

-- Usage aggregates per tenant (for dashboard)
CREATE TABLE IF NOT EXISTS usage_aggregates (
    id BIGSERIAL PRIMARY KEY,
    tenant_id VARCHAR(255) NOT NULL,
    date DATE NOT NULL,
    provider VARCHAR(50) NOT NULL,
    total_requests INT DEFAULT 0,
    total_prompt_tokens BIGINT DEFAULT 0,
    total_completion_tokens BIGINT DEFAULT 0,
    total_cost_usd DECIMAL(12, 6) DEFAULT 0,
    cache_hits INT DEFAULT 0,
    errors INT DEFAULT 0,
    UNIQUE(tenant_id, date, provider)
);

CREATE INDEX IF NOT EXISTS idx_usage_tenant_date ON usage_aggregates(tenant_id, date);

-- Tenant config: rate limits, allowed models, tool permissions
CREATE TABLE IF NOT EXISTS tenant_config (
    tenant_id VARCHAR(255) PRIMARY KEY,
    rate_limit_rpm INT DEFAULT 60,
    allowed_models TEXT[] DEFAULT ARRAY['gpt-4', 'gpt-4-turbo', 'gpt-3.5-turbo', 'claude-3-opus', 'claude-3-sonnet'],
    allow_tool_calls BOOLEAN DEFAULT TRUE,
    system_prompt_override TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Seed a default tenant for testing
INSERT INTO tenant_config (tenant_id, rate_limit_rpm)
VALUES ('default', 60)
ON CONFLICT (tenant_id) DO NOTHING;
