-- Migration for Dependent Masters: Departments & Holiday Lists

-- 1. Create the HR Departments Table
CREATE TABLE hr_departments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    created_by UUID,
    modified_by UUID,
    department_name VARCHAR NOT NULL UNIQUE,
    parent_department UUID REFERENCES hr_departments(id) ON DELETE SET NULL,
    company UUID NOT NULL REFERENCES hr_companies(id) ON DELETE CASCADE,
    is_group BOOLEAN NOT NULL DEFAULT false,
    disabled BOOLEAN NOT NULL DEFAULT false
);

CREATE INDEX idx_hr_departments_tenant_id ON hr_departments(tenant_id);
CREATE INDEX idx_hr_departments_company ON hr_departments(company);

ALTER TABLE hr_departments ENABLE ROW LEVEL SECURITY;
CREATE POLICY "tenant_isolation" ON hr_departments
    USING (tenant_id = current_setting('app.current_tenant_id', true)::UUID);

-- 2. Create the HR Holiday Lists Table
CREATE TABLE hr_holiday_lists (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    created_by UUID,
    modified_by UUID,
    holiday_list_name VARCHAR NOT NULL UNIQUE,
    from_date DATE NOT NULL,
    to_date DATE NOT NULL,
    company UUID NOT NULL REFERENCES hr_companies(id) ON DELETE CASCADE,
    weekly_off VARCHAR NOT NULL,
    total_holidays INTEGER NOT NULL DEFAULT 0
);

CREATE INDEX idx_hr_holiday_lists_tenant_id ON hr_holiday_lists(tenant_id);
CREATE INDEX idx_hr_holiday_lists_company ON hr_holiday_lists(company);

ALTER TABLE hr_holiday_lists ENABLE ROW LEVEL SECURITY;
CREATE POLICY "tenant_isolation" ON hr_holiday_lists
    USING (tenant_id = current_setting('app.current_tenant_id', true)::UUID);

-- 3. Create the HR Holidays Child Table
CREATE TABLE hr_holidays (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    created_by UUID,
    modified_by UUID,
    holiday_list_id UUID NOT NULL REFERENCES hr_holiday_lists(id) ON DELETE CASCADE,
    holiday_date DATE NOT NULL,
    description VARCHAR NOT NULL,
    weekly_off BOOLEAN NOT NULL DEFAULT false
);

CREATE INDEX idx_hr_holidays_tenant_id ON hr_holidays(tenant_id);
CREATE INDEX idx_hr_holidays_parent ON hr_holidays(holiday_list_id);

ALTER TABLE hr_holidays ENABLE ROW LEVEL SECURITY;
CREATE POLICY "tenant_isolation" ON hr_holidays
    USING (tenant_id = current_setting('app.current_tenant_id', true)::UUID);
