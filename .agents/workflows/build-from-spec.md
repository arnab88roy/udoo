---
description: Spec-driven development workflow. Use this to implement any new DocType from a .md spec file into a fully working module (Supabase migration + MetaEngine registry + Next.js page).
---

# Build From Spec — Spec-Driven Development Workflow

This workflow converts a `.md` spec file in `.agents/specs/hrms/` into a fully running Python FastAPI module.
Follow every step in order. Never skip a step. Never add fields not in the spec.

## STEP 1 — Read the Spec
Using `view_file`, read the target spec file (e.g., `.agents/specs/hrms/leave/leave_type_spec.md`).
Extract and list explicitly:
* Module Name (the DocType name, e.g., Leave Type)
* Type (Master / Transactional / Child Table)
* DocStatus (Yes / No — determines if docstatus column is needed)
* Dependencies (every `Link ->` line)
* All Schema Fields (fieldname -> fieldtype -> required -> read_only -> options)
* All Child Tables (each child DocType name and the parent field name)

Also read `_relationships.md` to confirm the creation order and that all dependency layers are satisfied before this DocType.
Stop here if the spec is ambiguous or the Dependencies section references a DocType that has no spec file yet.

## STEP 2 — Validate Dependencies in Supabase
For every `Link ->` dependency listed in the spec:
* Confirm the target table already exists in Supabase by checking `supabase/migrations/` for a relevant migration file, OR use your MCP database tool to inspect the live schema.
* If a dependency table is missing, STOP. Inform the user they must run the workflow for the dependency first.

## STEP 3 — Write the Supabase Migration
Create a new file: `supabase/migrations/<timestamp>_create_<table_name>.sql`
Naming convention for table names:
* Module prefix + snake_case DocType name
* Examples: `hr_leave_types`, `hr_leave_applications`, `hr_employees`

**Standard columns to ALWAYS include (these are system columns):**
```sql
id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
tenant_id           UUID NOT NULL, -- (For RLS)
created_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
updated_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
created_by          UUID,
modified_by         UUID
```

**If `DocStatus: Yes` — also add:**
```sql
docstatus           SMALLINT NOT NULL DEFAULT 0 CHECK (docstatus IN (0, 1, 2))
-- 0=Draft, 1=Submitted, 2=Cancelled
```

**RLS Policy — Add at the bottom of every migration:**
```sql
ALTER TABLE <table_name> ENABLE ROW LEVEL SECURITY;

CREATE POLICY "tenant_isolation" ON <table_name>
    USING (tenant_id = current_setting('app.current_tenant_id')::UUID);
```

## STEP 4 — Create SQLAlchemy Models
Create (or append to) the model file for the module: `backend/app/modules/<module_slug>/models.py`
* Map the SQL columns strictly to SQLAlchemy ORM columns.
* Use UUID for foreign keys linking to other modules.
* Establish `relationship()` for child tables. Ensure child tables use `cascade="all, delete-orphan"`.

## STEP 5 — Create Pydantic Schemas
Create the schema file: `backend/app/modules/<module_slug>/schemas.py`
* Create a Base schema containing all fields from the spec.
* Create a Create schema (excluding id, created_at, tenant_id).
* Create an Update schema (with optional fields).
* Create a Response schema (including id, docstatus, and system timestamps) setting `model_config = ConfigDict(from_attributes=True)`.

## STEP 6 — Create FastAPI Router & Endpoints
Create the router file: `backend/app/modules/<module_slug>/router.py`
* Initialize `APIRouter(prefix="/<module_slug>", tags=["<Module Name>"])`.
* Implement standard CRUD endpoints (GET list, GET by ID, POST create, PUT update, DELETE).
* Mandatory Dependency: Every endpoint MUST inject the database session and the tenant_id to enforce RLS.
* If DocStatus: Yes, create a specific endpoint for state transitions (e.g., `POST /{id}/submit` to change docstatus from 0 to 1).

## STEP 7 — Register the Router
Open `backend/app/main.py` and register the newly created module router to the main FastAPI application.
```python
from app.modules.<module_slug>.router import router as <module_slug>_router
app.include_router(<module_slug>_router)
```

## STEP 8 — Verify
Run through this checklist before marking the task complete:
* [ ] Migration file exists in `supabase/migrations/` and has no syntax errors.
* [ ] RLS policy is present in the migration.
* [ ] SQLAlchemy model contains exactly the fields from the spec — no extras.
* [ ] Pydantic schemas correctly validate required vs optional fields.
* [ ] FastAPI router is fully implemented and registered in `main.py`.
* [ ] Run `pytest` or `fastapi dev` to confirm zero Python runtime errors or circular import issues.

### Why these changes were necessary:
1. **Removed all Next.js/React Steps:** Steps 6 and 7 in your images told the agent to build `.tsx` files and Next.js server actions. I replaced these with Step 4, 5, and 6 to build **SQLAlchemy models, Pydantic schemas, and FastAPI routers.**
2. **Removed Zod:** I replaced the Zod schema generation with Pydantic, which is the native, highly-performant validation layer for FastAPI.
3. **Kept the DB/SQL logic:** Your Supabase migration instructions (Step 3) were excellent, especially the RLS injection, so I preserved those exactly.