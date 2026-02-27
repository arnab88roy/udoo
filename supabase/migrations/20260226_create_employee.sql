-- Migration for Employee Master and its Child Tables

-- 1. Create the HR Employees Table
CREATE TABLE hr_employees (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    created_by UUID,
    modified_by UUID,
    
    -- Basic Info
    naming_series VARCHAR DEFAULT 'HR-EMP-',
    first_name VARCHAR NOT NULL,
    middle_name VARCHAR,
    last_name VARCHAR,
    employee_name VARCHAR, -- Computed
    salutation_id UUID REFERENCES hr_salutations(id) ON DELETE SET NULL,
    gender_id UUID NOT NULL REFERENCES hr_genders(id) ON DELETE RESTRICT,
    date_of_birth DATE NOT NULL,
    image TEXT,
    employee_number VARCHAR,
    
    -- Status
    status VARCHAR NOT NULL DEFAULT 'Active' CHECK (status IN ('Active', 'Inactive', 'Suspended', 'Left')),
    user_id UUID REFERENCES hr_users(id) ON DELETE SET NULL,
    
    -- Company Details
    company_id UUID NOT NULL REFERENCES hr_companies(id) ON DELETE RESTRICT,
    department_id UUID REFERENCES hr_departments(id) ON DELETE SET NULL,
    designation_id UUID REFERENCES hr_designations(id) ON DELETE SET NULL,
    reports_to_id UUID REFERENCES hr_employees(id) ON DELETE SET NULL,
    branch_id UUID REFERENCES hr_branches(id) ON DELETE SET NULL,
    employment_type_id UUID REFERENCES hr_employment_types(id) ON DELETE SET NULL,
    employee_grade_id UUID REFERENCES hr_employee_grades(id) ON DELETE SET NULL,
    
    -- Joining & Contract
    date_of_joining DATE NOT NULL,
    scheduled_confirmation_date DATE,
    final_confirmation_date DATE,
    contract_end_date DATE,
    notice_number_of_days INTEGER,
    date_of_retirement DATE,
    
    -- Attendance & Leave
    attendance_device_id VARCHAR UNIQUE,
    holiday_list_id UUID REFERENCES hr_holiday_lists(id) ON DELETE SET NULL,
    
    -- Salary
    salary_mode VARCHAR CHECK (salary_mode IN ('Bank', 'Cash', 'Cheque')),
    salary_currency_id UUID REFERENCES hr_currencies(id) ON DELETE SET NULL,
    ctc NUMERIC(18, 2),
    bank_name VARCHAR,
    bank_ac_no VARCHAR,
    iban VARCHAR,
    
    -- Contact
    cell_number VARCHAR,
    company_email VARCHAR,
    personal_email VARCHAR,
    prefered_contact_email VARCHAR CHECK (prefered_contact_email IN ('Company Email', 'Personal Email', 'User ID')),
    prefered_email VARCHAR,
    unsubscribed BOOLEAN DEFAULT false,
    
    -- Address
    current_address TEXT,
    current_accommodation_type VARCHAR CHECK (current_accommodation_type IN ('Rented', 'Owned')),
    permanent_address TEXT,
    permanent_accommodation_type VARCHAR CHECK (permanent_accommodation_type IN ('Rented', 'Owned')),
    
    -- Emergency Contact
    person_to_be_contacted VARCHAR,
    emergency_phone_number VARCHAR,
    relation VARCHAR,
    
    -- Personal Details
    marital_status VARCHAR CHECK (marital_status IN ('Single', 'Married', 'Divorced', 'Widowed')),
    blood_group VARCHAR CHECK (blood_group IN ('A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-')),
    family_background TEXT,
    health_details TEXT,
    passport_number VARCHAR,
    passport_date_of_issue DATE,
    passport_valid_upto DATE,
    passport_place_of_issue VARCHAR,
    bio TEXT,
    
    -- Exit Info
    resignation_letter_date DATE,
    relieving_date DATE,
    reason_for_leaving TEXT,
    leave_encashed VARCHAR CHECK (leave_encashed IN ('Yes', 'No')),
    encashment_date DATE
);

CREATE INDEX idx_hr_employees_tenant_id ON hr_employees(tenant_id);
CREATE INDEX idx_hr_employees_company ON hr_employees(company_id);
CREATE INDEX idx_hr_employees_status ON hr_employees(status);

ALTER TABLE hr_employees ENABLE ROW LEVEL SECURITY;
CREATE POLICY "tenant_isolation" ON hr_employees
    USING (tenant_id = current_setting('app.current_tenant_id', true)::UUID);

-- 2. Create the HR Employee Educations Table
CREATE TABLE hr_employee_educations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    employee_id UUID NOT NULL REFERENCES hr_employees(id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    
    school_univ TEXT,
    qualification VARCHAR,
    level VARCHAR CHECK (level IN ('Graduate', 'Post Graduate', 'Under Graduate')),
    year_of_passing INTEGER,
    class_per VARCHAR,
    maj_opt_subj TEXT
);

CREATE INDEX idx_hr_employee_educations_employee ON hr_employee_educations(employee_id);

ALTER TABLE hr_employee_educations ENABLE ROW LEVEL SECURITY;
CREATE POLICY "tenant_isolation" ON hr_employee_educations
    USING (tenant_id = current_setting('app.current_tenant_id', true)::UUID);

-- 3. Create the HR Employee External Work History Table
CREATE TABLE hr_employee_external_work_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    employee_id UUID NOT NULL REFERENCES hr_employees(id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    
    company_name VARCHAR,
    designation VARCHAR,
    salary NUMERIC(18, 2),
    address TEXT,
    contact VARCHAR,
    total_experience VARCHAR
);

CREATE INDEX idx_hr_employee_ext_work_employee ON hr_employee_external_work_history(employee_id);

ALTER TABLE hr_employee_external_work_history ENABLE ROW LEVEL SECURITY;
CREATE POLICY "tenant_isolation" ON hr_employee_external_work_history
    USING (tenant_id = current_setting('app.current_tenant_id', true)::UUID);

-- 4. Create the HR Employee Internal Work History Table
CREATE TABLE hr_employee_internal_work_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    employee_id UUID NOT NULL REFERENCES hr_employees(id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    
    branch_id UUID REFERENCES hr_branches(id) ON DELETE SET NULL,
    department_id UUID REFERENCES hr_departments(id) ON DELETE SET NULL,
    designation_id UUID REFERENCES hr_designations(id) ON DELETE SET NULL,
    from_date DATE,
    to_date DATE
);

CREATE INDEX idx_hr_employee_int_work_employee ON hr_employee_internal_work_history(employee_id);

ALTER TABLE hr_employee_internal_work_history ENABLE ROW LEVEL SECURITY;
CREATE POLICY "tenant_isolation" ON hr_employee_internal_work_history
    USING (tenant_id = current_setting('app.current_tenant_id', true)::UUID);
