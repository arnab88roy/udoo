---
name: rls-security
description: Mandatory rules for implementing Row-Level Security in Postgres and FastAPI.
---

# Skill: RLS Enforcement (Supabase + FastAPI)

## 1. Migration Rules (Alembic — Single Source of Truth)
- **Alembic is the ONLY migration system.** Never create or modify tables via Supabase SQL editor or raw SQL files.
- Every `op.create_table()` in an Alembic migration MUST be followed by RLS enablement:
  ```python
  op.execute("ALTER TABLE <table_name> ENABLE ROW LEVEL SECURITY;")
  op.execute("""
      CREATE POLICY "tenant_isolation" ON <table_name>
      USING (tenant_id = current_setting('app.current_tenant_id', true)::UUID);
  """)
  ```
- The `true` flag in `current_setting(..., true)` prevents errors when the setting is not yet defined.

## 2. FastAPI Session Injection
- Every endpoint must inject `tenant_id` from the JWT via `Depends(get_tenant_id)`.
- The `tenant_id` must be set as a Postgres session variable before queries execute:
  ```python
  await db.execute(text("SELECT set_config('app.current_tenant_id', :tid, true)"), {"tid": str(tenant_id)})
  ```
- This ensures the RLS policy is triggered at the database level, not just application level.

## 3. SQLAlchemy Model Rule
- Every model must include:
  ```python
  tenant_id = Column(UUID(as_uuid=True), nullable=False, index=True)
  ```

## 4. Defense in Depth
- Application-level filtering (`WHERE tenant_id = :tenant_id`) AND database-level RLS must both be active.
- Never rely on only one of these. Both layers must exist.
- If a query bypasses the application layer (background jobs, migrations, admin scripts), the DB-level RLS is the last line of defense.