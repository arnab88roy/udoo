-- ==========================================
-- 1. Universal Audit Logging Table
-- ==========================================
CREATE TABLE IF NOT EXISTS audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    table_name VARCHAR(255) NOT NULL,
    record_id UUID NOT NULL,
    action VARCHAR(10) NOT NULL CHECK (action IN ('INSERT', 'UPDATE', 'DELETE')),
    old_data JSONB,
    new_data JSONB,
    changed_by UUID REFERENCES auth.users(id),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Secure the audit_logs table (Only allow admins or backend service to read)
ALTER TABLE audit_logs ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Audit Logs are secure" ON audit_logs 
    FOR SELECT TO authenticated 
    USING (true); -- For now, allow authenticated reads. Can be restricted to Tenant Admins later.

-- ==========================================
-- 2. Generic Postgres Audit Trigger Function
-- ==========================================
-- This function automatically intercepts ANY change to ANY table it is attached to,
-- formats the OLD and NEW rows into JSON, and logs exactly who made the change.
CREATE OR REPLACE FUNCTION process_audit_log()
RETURNS TRIGGER AS $$
DECLARE
    user_id UUID;
BEGIN
    -- Extract the acting user gracefully from Supabase Auth
    user_id := auth.uid(); 

    IF (TG_OP = 'DELETE') THEN
        INSERT INTO audit_logs (table_name, record_id, action, old_data, changed_by)
        VALUES (TG_TABLE_NAME, OLD.id, TG_OP, row_to_json(OLD)::JSONB, user_id);
        RETURN OLD;
    ELSIF (TG_OP = 'UPDATE') THEN
        -- Only log if data actually changed
        IF row_to_json(OLD)::JSONB != row_to_json(NEW)::JSONB THEN
            INSERT INTO audit_logs (table_name, record_id, action, old_data, new_data, changed_by)
            VALUES (TG_TABLE_NAME, NEW.id, TG_OP, row_to_json(OLD)::JSONB, row_to_json(NEW)::JSONB, user_id);
        END IF;
        RETURN NEW;
    ELSIF (TG_OP = 'INSERT') THEN
        INSERT INTO audit_logs (table_name, record_id, action, new_data, changed_by)
        VALUES (TG_TABLE_NAME, NEW.id, TG_OP, row_to_json(NEW)::JSONB, user_id);
        RETURN NEW;
    END IF;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- ==========================================
-- 3. Inject `docstatus` into Core Tables
-- ==========================================
-- 0 = Draft, 1 = Submitted, 2 = Cancelled
-- Master data defaults to 1 (Submitted) because it usually doesn't require complex approval routing.

ALTER TABLE companies ADD COLUMN IF NOT EXISTS docstatus INTEGER DEFAULT 1 CHECK (docstatus IN (0, 1, 2));
ALTER TABLE departments ADD COLUMN IF NOT EXISTS docstatus INTEGER DEFAULT 1 CHECK (docstatus IN (0, 1, 2));
ALTER TABLE designations ADD COLUMN IF NOT EXISTS docstatus INTEGER DEFAULT 1 CHECK (docstatus IN (0, 1, 2));
ALTER TABLE branches ADD COLUMN IF NOT EXISTS docstatus INTEGER DEFAULT 1 CHECK (docstatus IN (0, 1, 2));
ALTER TABLE holiday_lists ADD COLUMN IF NOT EXISTS docstatus INTEGER DEFAULT 1 CHECK (docstatus IN (0, 1, 2));
ALTER TABLE hr_employees ADD COLUMN IF NOT EXISTS docstatus INTEGER DEFAULT 1 CHECK (docstatus IN (0, 1, 2));

-- ==========================================
-- 4. Apply Audit Triggers to Core Tables
-- ==========================================

CREATE TRIGGER audit_companies_trigger AFTER INSERT OR UPDATE OR DELETE ON companies FOR EACH ROW EXECUTE FUNCTION process_audit_log();
CREATE TRIGGER audit_departments_trigger AFTER INSERT OR UPDATE OR DELETE ON departments FOR EACH ROW EXECUTE FUNCTION process_audit_log();
CREATE TRIGGER audit_designations_trigger AFTER INSERT OR UPDATE OR DELETE ON designations FOR EACH ROW EXECUTE FUNCTION process_audit_log();
CREATE TRIGGER audit_branches_trigger AFTER INSERT OR UPDATE OR DELETE ON branches FOR EACH ROW EXECUTE FUNCTION process_audit_log();
CREATE TRIGGER audit_holiday_lists_trigger AFTER INSERT OR UPDATE OR DELETE ON holiday_lists FOR EACH ROW EXECUTE FUNCTION process_audit_log();
CREATE TRIGGER audit_hr_employees_trigger AFTER INSERT OR UPDATE OR DELETE ON hr_employees FOR EACH ROW EXECUTE FUNCTION process_audit_log();
