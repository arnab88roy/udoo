-- Migration for Employee Grade

CREATE TABLE hr_employee_grades (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    created_by UUID,
    modified_by UUID,
    grade_name VARCHAR NOT NULL UNIQUE,
    default_base_pay NUMERIC(18, 2),
    currency_id UUID REFERENCES hr_currencies(id) ON DELETE SET NULL
);

CREATE INDEX idx_hr_employee_grades_tenant_id ON hr_employee_grades(tenant_id);

ALTER TABLE hr_employee_grades ENABLE ROW LEVEL SECURITY;
CREATE POLICY "tenant_isolation" ON hr_employee_grades
    USING (tenant_id = current_setting('app.current_tenant_id', true)::UUID);
