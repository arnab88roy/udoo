-- ==========================================
-- PHASE 2: HUB ENHANCEMENT (FRAPPE ALIGNMENT)
-- ==========================================

-- 1. Aligning Companies (Tenants) with ERPNext needs
ALTER TABLE companies 
ADD COLUMN base_currency VARCHAR(3) DEFAULT 'USD',
ADD COLUMN country VARCHAR(100),
ADD COLUMN tax_id VARCHAR(50);

-- 2. Aligning Contacts (The Hub) to serve as the master record for Employee/Customer data
ALTER TABLE contacts 
ADD COLUMN designation VARCHAR(150),
ADD COLUMN gender VARCHAR(50),
ADD COLUMN status VARCHAR(50) DEFAULT 'Active';

-- 3. Storage Bucket Configuration for Polymorphic Attachments
-- Ensure the storage extension and schema exist (handled natively by Supabase, but good practice to ensure bucket)
INSERT INTO storage.buckets (id, name, public) 
VALUES ('attachments', 'attachments', false)
ON CONFLICT (id) DO NOTHING;

-- Note: In a full production Supabase instance, Storage RLS policies would be applied here 
-- to ensure users can only access objects linked to their tenant's file_attachments records.
-- Example:
-- CREATE POLICY "Tenant Storage Access" ON storage.objects FOR SELECT 
-- USING (bucket_id = 'attachments' AND ...);
