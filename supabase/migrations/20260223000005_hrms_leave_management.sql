-- ==========================================
-- Microscopic Schema Replication: Leave Management Vertical Slice
-- Based directly on Frappe HRMS JSON DocType structures.
-- ==========================================

-- 1. Leave Type (Setup Data)
-- reference/hrms/hrms/hr/doctype/leave_type/leave_type.json
CREATE TABLE IF NOT EXISTS hr_leave_types (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id UUID NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    
    leave_type_name VARCHAR(140) NOT NULL UNIQUE,
    max_leaves_allowed NUMERIC(10, 2),
    applicable_after INTEGER, -- Working days
    max_continuous_days_allowed INTEGER,
    
    is_carry_forward BOOLEAN DEFAULT FALSE,
    is_lwp BOOLEAN DEFAULT FALSE, -- Leave Without Pay
    is_optional_leave BOOLEAN DEFAULT FALSE,
    allow_negative BOOLEAN DEFAULT FALSE,
    include_holiday BOOLEAN DEFAULT FALSE,
    is_compensatory BOOLEAN DEFAULT FALSE,
    allow_encashment BOOLEAN DEFAULT FALSE,
    is_earned_leave BOOLEAN DEFAULT FALSE,
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 2. Leave Policy & Child Table (Setup Data)
-- reference/hrms/hrms/hr/doctype/leave_policy/leave_policy.json
CREATE TABLE IF NOT EXISTS hr_leave_policies (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id UUID NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    title VARCHAR(140) NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Frappe Child Table implementations mandate a cascading FK to the parent
CREATE TABLE IF NOT EXISTS hr_leave_policy_details (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    leave_policy_id UUID NOT NULL REFERENCES hr_leave_policies(id) ON DELETE CASCADE,
    leave_type_id UUID NOT NULL REFERENCES hr_leave_types(id) ON DELETE RESTRICT,
    annual_allocation NUMERIC(10, 2) NOT NULL DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 3. Leave Policy Assignment (Transactional)
-- reference/hrms/hrms/hr/doctype/leave_policy_assignment/leave_policy_assignment.json
CREATE TABLE IF NOT EXISTS hr_leave_policy_assignments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    docstatus INTEGER DEFAULT 0 CHECK (docstatus IN (0, 1, 2)), -- 0=Draft, 1=Submitted, 2=Cancelled
    company_id UUID NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    employee_id UUID NOT NULL REFERENCES hr_employees(id) ON DELETE CASCADE,
    leave_policy_id UUID NOT NULL REFERENCES hr_leave_policies(id) ON DELETE RESTRICT,
    
    assignment_based_on VARCHAR(50) CHECK (assignment_based_on IN ('Leave Period', 'Joining Date')),
    effective_from DATE NOT NULL,
    effective_to DATE,
    carry_forward BOOLEAN DEFAULT FALSE,
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 4. Leave Allocation (Transactional)
-- reference/hrms/hrms/hr/doctype/leave_allocation/leave_allocation.json
CREATE TABLE IF NOT EXISTS hr_leave_allocations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    docstatus INTEGER DEFAULT 0 CHECK (docstatus IN (0, 1, 2)),
    company_id UUID NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    employee_id UUID NOT NULL REFERENCES hr_employees(id) ON DELETE CASCADE,
    leave_type_id UUID NOT NULL REFERENCES hr_leave_types(id) ON DELETE RESTRICT,
    
    from_date DATE NOT NULL,
    to_date DATE NOT NULL,
    
    new_leaves_allocated NUMERIC(10, 2) NOT NULL DEFAULT 0,
    carry_forward BOOLEAN DEFAULT FALSE,
    unused_leaves NUMERIC(10, 2) DEFAULT 0,
    total_leaves_allocated NUMERIC(10, 2) NOT NULL DEFAULT 0,
    
    leave_policy_assignment_id UUID REFERENCES hr_leave_policy_assignments(id) ON DELETE SET NULL,
    description TEXT,
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 5. Leave Application (Transactional)
-- reference/hrms/hrms/hr/doctype/leave_application/leave_application.json
CREATE TABLE IF NOT EXISTS hr_leave_applications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    docstatus INTEGER DEFAULT 0 CHECK (docstatus IN (0, 1, 2)),
    company_id UUID NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    employee_id UUID NOT NULL REFERENCES hr_employees(id) ON DELETE CASCADE,
    leave_type_id UUID NOT NULL REFERENCES hr_leave_types(id) ON DELETE RESTRICT,
    
    from_date DATE NOT NULL,
    to_date DATE NOT NULL,
    half_day BOOLEAN DEFAULT FALSE,
    half_day_date DATE,
    total_leave_days NUMERIC(10, 2) NOT NULL,
    description TEXT,
    
    leave_approver_id UUID REFERENCES auth.users(id) ON DELETE SET NULL,
    status VARCHAR(50) DEFAULT 'Open' CHECK (status IN ('Open', 'Approved', 'Rejected', 'Cancelled')),
    posting_date DATE DEFAULT CURRENT_DATE,
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ==========================================
-- Row Level Security (RLS) for Tenant Isolation
-- ==========================================
ALTER TABLE hr_leave_types ENABLE ROW LEVEL SECURITY;
ALTER TABLE hr_leave_policies ENABLE ROW LEVEL SECURITY;
ALTER TABLE hr_leave_policy_details ENABLE ROW LEVEL SECURITY;
ALTER TABLE hr_leave_policy_assignments ENABLE ROW LEVEL SECURITY;
ALTER TABLE hr_leave_allocations ENABLE ROW LEVEL SECURITY;
ALTER TABLE hr_leave_applications ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Tenant Isolation: hr_leave_types" ON hr_leave_types FOR ALL TO authenticated USING ( company_id = auth.company_id() );
CREATE POLICY "Tenant Isolation: hr_leave_policies" ON hr_leave_policies FOR ALL TO authenticated USING ( company_id = auth.company_id() );
-- Child table inherits policy by joining parent but simpler just to use the existing RLS logic in Supabase if we trust backend, but we'll add it explicitly where possible.
-- For details without company_id, we look up via the parent (or we could just add company_id to details, but Frappe joins it).
CREATE POLICY "Tenant Isolation: hr_leave_policy_details" ON hr_leave_policy_details FOR ALL TO authenticated USING ( 
    leave_policy_id IN (SELECT id FROM hr_leave_policies WHERE company_id = auth.company_id()) 
);
CREATE POLICY "Tenant Isolation: hr_leave_policy_assignments" ON hr_leave_policy_assignments FOR ALL TO authenticated USING ( company_id = auth.company_id() );
CREATE POLICY "Tenant Isolation: hr_leave_allocations" ON hr_leave_allocations FOR ALL TO authenticated USING ( company_id = auth.company_id() );
CREATE POLICY "Tenant Isolation: hr_leave_applications" ON hr_leave_applications FOR ALL TO authenticated USING ( company_id = auth.company_id() );

-- ==========================================
-- Apply Universal Audit Triggers
-- ==========================================
CREATE TRIGGER audit_hr_leave_policy_assignments_trigger AFTER INSERT OR UPDATE OR DELETE ON hr_leave_policy_assignments FOR EACH ROW EXECUTE FUNCTION process_audit_log();
CREATE TRIGGER audit_hr_leave_allocations_trigger AFTER INSERT OR UPDATE OR DELETE ON hr_leave_allocations FOR EACH ROW EXECUTE FUNCTION process_audit_log();
CREATE TRIGGER audit_hr_leave_applications_trigger AFTER INSERT OR UPDATE OR DELETE ON hr_leave_applications FOR EACH ROW EXECUTE FUNCTION process_audit_log();
