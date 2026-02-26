---
name: rls-security
description: Mandatory rules for implementing Row-Level Security in Postgres and FastAPI.
---

# Skill: Supabase RLS Enforcement

1. **Database Migrations:** Every single table creation script in `supabase/migrations/` MUST end with:
   `ALTER TABLE <table_name> ENABLE ROW LEVEL SECURITY;`
   `CREATE POLICY "tenant_isolation" ON <table_name> USING (tenant_id = current_setting('app.current_tenant_id')::UUID);`
2. **FastAPI Injection:** Every FastAPI endpoint must inject the `tenant_id` (extracted from the JWT token) into the Postgres session context before executing any queries, ensuring the RLS policy is triggered.
3. **Model Columns:** Every SQLAlchemy model must include `tenant_id = Column(UUID(as_uuid=True), nullable=False, index=True)`.