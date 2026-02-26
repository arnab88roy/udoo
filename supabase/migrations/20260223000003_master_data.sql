-- ==========================================
-- PHASE 2.5: ORGANIZATIONAL MASTER DATA & SYSTEM MASTERS
-- ==========================================

-- 1. System Masters (Independent of Tenants)
CREATE TABLE IF NOT EXISTS countries (
  code VARCHAR(2) PRIMARY KEY, -- ISO 3166-1 alpha-2
  name VARCHAR(100) NOT NULL,
  date_format VARCHAR(20) DEFAULT 'YYYY-MM-DD',
  time_zone VARCHAR(50) DEFAULT 'UTC'
);

CREATE TABLE IF NOT EXISTS currencies (
  code VARCHAR(3) PRIMARY KEY, -- ISO 4217
  name VARCHAR(50) NOT NULL,
  symbol VARCHAR(10),
  fraction VARCHAR(20),
  fraction_units INT DEFAULT 100
);

-- 2. Tenant Extensions for Master Defaults
ALTER TABLE companies 
  ADD COLUMN IF NOT EXISTS default_currency VARCHAR(3) REFERENCES currencies(code),
  ADD COLUMN IF NOT EXISTS country VARCHAR(2) REFERENCES countries(code);

-- 3. Organizational Master Data (Tenant Isolated)

-- Branches (Physical or Logical Locations)
CREATE TABLE branches (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  company_id UUID NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
  branch_name VARCHAR(255) NOT NULL,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(company_id, branch_name)
);

-- Departments (Hierarchical tree structure for org charts)
CREATE TABLE departments (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  company_id UUID NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
  parent_department_id UUID REFERENCES departments(id) ON DELETE SET NULL,
  department_name VARCHAR(255) NOT NULL,
  is_group BOOLEAN DEFAULT false, -- True if it acts merely as a folder for sub-departments
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(company_id, department_name)
);

-- Designations (Job Titles without specific opening metadata)
CREATE TABLE designations (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  company_id UUID NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
  designation_name VARCHAR(255) NOT NULL,
  description TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(company_id, designation_name)
);

-- Holiday Lists (Vital for HR Leave and Payroll Calculation)
CREATE TABLE holiday_lists (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  company_id UUID NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
  holiday_list_name VARCHAR(255) NOT NULL,
  from_date DATE NOT NULL,
  to_date DATE NOT NULL,
  weekly_off VARCHAR(20) DEFAULT 'Sunday', -- Can be an array in full spec
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(company_id, holiday_list_name)
);

CREATE TABLE holidays (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  holiday_list_id UUID NOT NULL REFERENCES holiday_lists(id) ON DELETE CASCADE,
  holiday_date DATE NOT NULL,
  description VARCHAR(255) NOT NULL,
  UNIQUE(holiday_list_id, holiday_date)
);

-- ==========================================
-- ROW LEVEL SECURITY (RLS) FOR MASTER DATA
-- ==========================================

-- Enable RLS
ALTER TABLE branches ENABLE ROW LEVEL SECURITY;
ALTER TABLE departments ENABLE ROW LEVEL SECURITY;
ALTER TABLE designations ENABLE ROW LEVEL SECURITY;
ALTER TABLE holiday_lists ENABLE ROW LEVEL SECURITY;
ALTER TABLE holidays ENABLE ROW LEVEL SECURITY;
-- (Countries and Currencies are global, read-only for all authenticated users, so RLS operates differently there)

-- Global Reference Data Policies (Read Only for authenticated users)
CREATE POLICY "Anyone can read countries" ON countries FOR SELECT TO authenticated USING (true);
CREATE POLICY "Anyone can read currencies" ON currencies FOR SELECT TO authenticated USING (true);

-- Tenant Isolation Policies
CREATE POLICY "Tenant Isolation: Branches" ON branches FOR ALL TO authenticated
USING ( company_id = auth.company_id() );

CREATE POLICY "Tenant Isolation: Departments" ON departments FOR ALL TO authenticated
USING ( company_id = auth.company_id() );

CREATE POLICY "Tenant Isolation: Designations" ON designations FOR ALL TO authenticated
USING ( company_id = auth.company_id() );

CREATE POLICY "Tenant Isolation: Holiday Lists" ON holiday_lists FOR ALL TO authenticated
USING ( company_id = auth.company_id() );

CREATE POLICY "Tenant Isolation: Holidays" ON holidays FOR ALL TO authenticated
USING ( 
  holiday_list_id IN (SELECT id FROM holiday_lists WHERE company_id = auth.company_id()) 
);

-- NOTE: We will hook these up into hr_employees and other entities in the next migration step securely.
