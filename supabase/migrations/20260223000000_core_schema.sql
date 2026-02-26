-- Enable necessary extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ==========================================
-- 1. CORE ENTITIES
-- ==========================================

-- Companies (Tenants)
CREATE TABLE companies (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  name VARCHAR(255) NOT NULL,
  domain VARCHAR(255) UNIQUE,
  subscription_plan VARCHAR(50) DEFAULT 'free',
  active_modules TEXT[] DEFAULT '{}',
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Contacts (The Hub)
CREATE TABLE contacts (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  company_id UUID NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
  user_id UUID REFERENCES auth.users(id) ON DELETE SET NULL, -- Optional link to auth
  first_name VARCHAR(100) NOT NULL,
  last_name VARCHAR(100) NOT NULL,
  email VARCHAR(255),
  phone VARCHAR(50),
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- User Roles (RBAC mapping)
CREATE TABLE user_roles (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  company_id UUID NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  role VARCHAR(50) NOT NULL DEFAULT 'employee', -- 'owner', 'admin_hr', 'employee', etc.
  created_at TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(company_id, user_id)
);

-- File Attachments (Polymorphic config)
CREATE TABLE file_attachments (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  company_id UUID NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
  entity_type VARCHAR(100) NOT NULL, -- e.g., 'expense', 'employee_resume'
  entity_id UUID NOT NULL,
  file_url TEXT NOT NULL,
  file_name VARCHAR(255),
  uploaded_by UUID REFERENCES auth.users(id) ON DELETE SET NULL,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- System Audit Logs (CRITICAL)
CREATE TABLE audit_logs (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  company_id UUID NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
  user_id UUID REFERENCES auth.users(id) ON DELETE SET NULL,
  action_type VARCHAR(100) NOT NULL, -- e.g., 'CREATE_INVOICE', 'UPDATE_EMPLOYEE'
  entity_type VARCHAR(100) NOT NULL,
  entity_id UUID NOT NULL,
  old_data JSONB,
  new_data JSONB,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ==========================================
-- 2. ROW LEVEL SECURITY (RLS)
-- ==========================================

ALTER TABLE companies ENABLE ROW LEVEL SECURITY;
ALTER TABLE contacts ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_roles ENABLE ROW LEVEL SECURITY;
ALTER TABLE file_attachments ENABLE ROW LEVEL SECURITY;
ALTER TABLE audit_logs ENABLE ROW LEVEL SECURITY;

-- JWT Function helper for cleaner RLS
CREATE OR REPLACE FUNCTION auth.company_id() RETURNS UUID AS $$
  SELECT NULLIF(current_setting('request.jwt.claims', true)::json->'app_metadata'->>'company_id', '')::UUID;
$$ LANGUAGE SQL STABLE;

CREATE OR REPLACE FUNCTION auth.user_role() RETURNS TEXT AS $$
  SELECT current_setting('request.jwt.claims', true)::json->'app_metadata'->>'user_role';
$$ LANGUAGE SQL STABLE;

-- RLS Policies for Contacts
CREATE POLICY "Tenant Isolation Policy for Contacts" ON contacts
  FOR ALL USING (company_id = auth.company_id());

-- RLS Policies for User Roles
CREATE POLICY "Tenant Isolation Policy for Roles" ON user_roles
  FOR ALL USING (company_id = auth.company_id());

-- RLS Policies for File Attachments
CREATE POLICY "Tenant Isolation Policy for Files" ON file_attachments
  FOR ALL USING (company_id = auth.company_id());

-- RLS Policies for Audit Logs (Only owners/admins can read, everyone writes their own implicitly via API but direct access is restricted)
CREATE POLICY "Tenant Isolation Policy for Audit Logs" ON audit_logs
  FOR SELECT USING (company_id = auth.company_id() AND auth.user_role() IN ('owner', 'admin_sys'));
CREATE POLICY "Allow Insert Audit Logs" ON audit_logs
  FOR INSERT WITH CHECK (company_id = auth.company_id());

-- RLS Policies for Companies (Users can see their own company details)
CREATE POLICY "View Own Company" ON companies
  FOR SELECT USING (id = auth.company_id());
