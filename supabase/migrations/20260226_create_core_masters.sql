-- Create the HR Companies Table
CREATE TABLE hr_companies (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    created_by UUID,
    modified_by UUID,
    company_name VARCHAR NOT NULL UNIQUE,
    abbr VARCHAR NOT NULL UNIQUE,
    domain VARCHAR
);

CREATE INDEX idx_hr_companies_tenant_id ON hr_companies(tenant_id);
CREATE INDEX idx_hr_companies_company_name ON hr_companies(company_name);

ALTER TABLE hr_companies ENABLE ROW LEVEL SECURITY;
CREATE POLICY "tenant_isolation" ON hr_companies
    USING (tenant_id = current_setting('app.current_tenant_id', true)::UUID);

-- Create the HR Branches Table
CREATE TABLE hr_branches (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    created_by UUID,
    modified_by UUID,
    branch VARCHAR NOT NULL UNIQUE
);

CREATE INDEX idx_hr_branches_tenant_id ON hr_branches(tenant_id);
CREATE INDEX idx_hr_branches_branch ON hr_branches(branch);

ALTER TABLE hr_branches ENABLE ROW LEVEL SECURITY;
CREATE POLICY "tenant_isolation" ON hr_branches
    USING (tenant_id = current_setting('app.current_tenant_id', true)::UUID);

-- Create the HR Genders Table
CREATE TABLE hr_genders (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    created_by UUID,
    modified_by UUID,
    name VARCHAR NOT NULL UNIQUE
);

CREATE INDEX idx_hr_genders_tenant_id ON hr_genders(tenant_id);
CREATE INDEX idx_hr_genders_name ON hr_genders(name);

ALTER TABLE hr_genders ENABLE ROW LEVEL SECURITY;
CREATE POLICY "tenant_isolation" ON hr_genders
    USING (tenant_id = current_setting('app.current_tenant_id', true)::UUID);

-- Create the HR Salutations Table
CREATE TABLE hr_salutations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    created_by UUID,
    modified_by UUID,
    name VARCHAR NOT NULL UNIQUE
);

CREATE INDEX idx_hr_salutations_tenant_id ON hr_salutations(tenant_id);
CREATE INDEX idx_hr_salutations_name ON hr_salutations(name);

ALTER TABLE hr_salutations ENABLE ROW LEVEL SECURITY;
CREATE POLICY "tenant_isolation" ON hr_salutations
    USING (tenant_id = current_setting('app.current_tenant_id', true)::UUID);

-- Create the HR Employment Types Table
CREATE TABLE hr_employment_types (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    created_by UUID,
    modified_by UUID,
    employee_type_name VARCHAR NOT NULL UNIQUE
);

CREATE INDEX idx_hr_employment_types_tenant_id ON hr_employment_types(tenant_id);
CREATE INDEX idx_hr_employment_types_employee_type_name ON hr_employment_types(employee_type_name);

ALTER TABLE hr_employment_types ENABLE ROW LEVEL SECURITY;
CREATE POLICY "tenant_isolation" ON hr_employment_types
    USING (tenant_id = current_setting('app.current_tenant_id', true)::UUID);

-- Create the HR Designations Table
CREATE TABLE hr_designations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    created_by UUID,
    modified_by UUID,
    designation_name VARCHAR NOT NULL UNIQUE,
    description TEXT
);

CREATE INDEX idx_hr_designations_tenant_id ON hr_designations(tenant_id);
CREATE INDEX idx_hr_designations_designation_name ON hr_designations(designation_name);

ALTER TABLE hr_designations ENABLE ROW LEVEL SECURITY;
CREATE POLICY "tenant_isolation" ON hr_designations
    USING (tenant_id = current_setting('app.current_tenant_id', true)::UUID);

-- Create the HR Skills Table
CREATE TABLE hr_skills (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    created_by UUID,
    modified_by UUID,
    skill_name VARCHAR NOT NULL UNIQUE,
    description TEXT
);

CREATE INDEX idx_hr_skills_tenant_id ON hr_skills(tenant_id);
CREATE INDEX idx_hr_skills_skill_name ON hr_skills(skill_name);

ALTER TABLE hr_skills ENABLE ROW LEVEL SECURITY;
CREATE POLICY "tenant_isolation" ON hr_skills
    USING (tenant_id = current_setting('app.current_tenant_id', true)::UUID);
