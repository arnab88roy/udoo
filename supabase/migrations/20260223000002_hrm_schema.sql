-- ==========================================
-- PHASE 3: HRM MODULE SCHEMA
-- ==========================================

-- 1. HR Employees
-- Links a Master Contact to HR-specific employment details.
CREATE TABLE hr_employees (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  company_id UUID NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
  contact_id UUID NOT NULL REFERENCES contacts(id) ON DELETE CASCADE,
  
  -- Master Data Relations
  department_id UUID REFERENCES departments(id),
  designation_id UUID REFERENCES designations(id),
  branch_id UUID REFERENCES branches(id),
  holiday_list_id UUID REFERENCES holiday_lists(id),
  
  -- Core HR Specifics
  employee_number VARCHAR(100) UNIQUE,
  status VARCHAR(50) DEFAULT 'Active', -- Active, Inactive, Suspended, Left
  date_of_joining DATE,
  date_of_leaving DATE,
  employment_type VARCHAR(50) DEFAULT 'Full-time', -- Full-time, Part-time, Contract, Commission
  reports_to UUID REFERENCES hr_employees(id), -- Self-referencing org structure, Suspended, Left
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 2. HR Leave Types
-- Configurable leave types per tenant (e.g., Sick Leave, Casual Leave)
CREATE TABLE hr_leave_types (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  company_id UUID NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
  name VARCHAR(100) NOT NULL,
  is_lwp BOOLEAN DEFAULT false, -- Is Leave Without Pay
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 3. HR Leave Applications
CREATE TABLE hr_leave_applications (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  company_id UUID NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
  employee_id UUID NOT NULL REFERENCES hr_employees(id) ON DELETE CASCADE,
  leave_type_id UUID NOT NULL REFERENCES hr_leave_types(id),
  from_date DATE NOT NULL,
  to_date DATE NOT NULL,
  half_day BOOLEAN DEFAULT false,
  total_leave_days NUMERIC(5,2) NOT NULL,
  status VARCHAR(50) DEFAULT 'Open', -- Open, Approved, Rejected, Cancelled
  reason TEXT,
  approver_id UUID REFERENCES auth.users(id) ON DELETE SET NULL,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 4. HR Attendance
CREATE TABLE hr_attendance (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  company_id UUID NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
  employee_id UUID NOT NULL REFERENCES hr_employees(id) ON DELETE CASCADE,
  attendance_date DATE NOT NULL,
  status VARCHAR(50) NOT NULL, -- Present, Absent, Half Day, On Leave, Work From Home
  in_time TIMESTAMPTZ,
  out_time TIMESTAMPTZ,
  working_hours NUMERIC(5,2),
  late_entry BOOLEAN DEFAULT false,
  early_exit BOOLEAN DEFAULT false,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(employee_id, attendance_date) -- Prevent duplicate attendance entries per day
);

-- 5. HR Salary Slips (Payroll)
CREATE TABLE hr_salary_slips (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  company_id UUID NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
  employee_id UUID NOT NULL REFERENCES hr_employees(id) ON DELETE CASCADE,
  posting_date DATE NOT NULL DEFAULT CURRENT_DATE,
  start_date DATE NOT NULL,
  end_date DATE NOT NULL,
  total_working_days NUMERIC(5,2) NOT NULL,
  leave_without_pay_days NUMERIC(5,2) DEFAULT 0,
  payment_days NUMERIC(5,2) NOT NULL,
  gross_pay NUMERIC(15,2) NOT NULL DEFAULT 0,
  total_deduction NUMERIC(15,2) NOT NULL DEFAULT 0,
  net_pay NUMERIC(15,2) NOT NULL DEFAULT 0,
  earnings JSONB DEFAULT '[]'::jsonb, -- Array of { description: string, amount: number }
  deductions JSONB DEFAULT '[]'::jsonb, -- Array of { description: string, amount: number }
  status VARCHAR(50) DEFAULT 'Draft', -- Draft, Submitted, Cancelled, Withheld
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ==========================================
-- ROW LEVEL SECURITY (RLS) FOR HRM
-- ==========================================

-- hr_employees
ALTER TABLE hr_employees ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Tenant isolation for hr_employees" ON hr_employees
  FOR ALL USING (company_id = auth.company_id());

-- hr_leave_types
ALTER TABLE hr_leave_types ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Tenant isolation for hr_leave_types" ON hr_leave_types
  FOR ALL USING (company_id = auth.company_id());

-- hr_leave_applications
ALTER TABLE hr_leave_applications ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Tenant isolation for hr_leave_applications" ON hr_leave_applications
  FOR ALL USING (company_id = auth.company_id());

-- hr_attendance
ALTER TABLE hr_attendance ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Tenant isolation for hr_attendance" ON hr_attendance
  FOR ALL USING (company_id = auth.company_id());

-- hr_salary_slips
ALTER TABLE hr_salary_slips ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Tenant isolation for hr_salary_slips" ON hr_salary_slips
  FOR ALL USING (company_id = auth.company_id());
