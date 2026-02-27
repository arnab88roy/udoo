-- Migration for System Dependencies: Currencies & Users

-- 1. Create the HR Currencies Table
CREATE TABLE hr_currencies (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    created_by UUID,
    modified_by UUID,
    currency_code VARCHAR NOT NULL UNIQUE,
    currency_symbol VARCHAR,
    fraction VARCHAR,
    fraction_units INTEGER DEFAULT 100
);

CREATE INDEX idx_hr_currencies_tenant_id ON hr_currencies(tenant_id);

ALTER TABLE hr_currencies ENABLE ROW LEVEL SECURITY;
CREATE POLICY "tenant_isolation" ON hr_currencies
    USING (tenant_id = current_setting('app.current_tenant_id', true)::UUID);

-- 2. Create the HR Users Table (Minimal for FK linkage)
CREATE TABLE hr_users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    email VARCHAR NOT NULL UNIQUE,
    full_name VARCHAR,
    is_active BOOLEAN DEFAULT true
);

CREATE INDEX idx_hr_users_tenant_id ON hr_users(tenant_id);

ALTER TABLE hr_users ENABLE ROW LEVEL SECURITY;
CREATE POLICY "tenant_isolation" ON hr_users
    USING (tenant_id = current_setting('app.current_tenant_id', true)::UUID);
