---
name: fastapi-crud-generator
description: Strict guidelines for generating FastAPI routers, Pydantic schemas, and SQLAlchemy models.
---

# Skill: FastAPI CRUD Generator

When writing Python code for a new module based on a spec, you MUST follow these rules:

## 1. SQLAlchemy Models
- Always inherit from `CoreMasterBase`.
- Use `UUID(as_uuid=True)` for all primary keys (`id`) and foreign keys.
- Every model must include `tenant_id = Column(UUID(as_uuid=True), nullable=False, index=True)`.
- Use `relationship()` with `cascade="all, delete-orphan"` for child tables within the same module.
- Never use JSONB for child table data — always relational tables.

## 2. Pydantic Schemas
- Always create `Base`, `Create`, `Update`, and `Response` schema classes.
- `Response` schema MUST include `model_config = ConfigDict(from_attributes=True)`.
- **Every field MUST have a `Field(description="...")` annotation.**
  This is mandatory — the VEDA AI agent reads field descriptions to understand context.
  Example:
  ```python
  attendance_date: date = Field(..., description="The date for which attendance is being marked. One record per employee per date.")
  docstatus: int = Field(0, description="Document state: 0=Draft, 1=Submitted, 2=Cancelled.")
  ```
- For nested responses that reference another module's entity (e.g. Employee inside Attendance),
  use a lightweight summary schema — NEVER the full response schema with all child tables.
  Example:
  ```python
  class EmployeeSummary(BaseModel):
      id: UUID
      employee_name: Optional[str]
      model_config = ConfigDict(from_attributes=True)
  ```

## 3. Routing
- Use `APIRouter(prefix="/<module-slug>", tags=["<Module Name>"])`.
  Prefix MUST be kebab-case (e.g. `attendance-requests`, not `attendanceRequests`).
- Register every new router in `main.py` under `/api` prefix.

## 4. Session & Security
- Inject `db: AsyncSession = Depends(get_db)` into every endpoint.
- Inject `tenant_id: UUID = Depends(get_tenant_id)` into every endpoint.
- Every list query MUST filter by `tenant_id`.
- Every single-record query MUST filter by both `id` AND `tenant_id`.

## 5. Eager Loading
- Always use `selectinload()` for relationship loading — never lazy load.
- For transactional records, only load what the response schema actually needs.
- Do NOT load full Employee child tables (education, work history) inside Leave or Attendance responses.
  Use `EmployeeSummary` instead.

## 6. Response Codes
- `POST` (create): `status_code=201`
- `GET`: `200`
- Not found: raise `HTTPException(status_code=404)`
- Validation/business rule error: raise `HTTPException(status_code=400)`

## 7. Pagination
- All `GET` list endpoints must include `skip: int = 0` and `limit: int = 100` parameters.

## 8. Error Handling
- Wrap all database writes in `try/except` blocks.
- Call `await db.rollback()` inside `except` before raising `HTTPException`.