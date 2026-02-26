---
name: fastapi-crud-generator
description: Strict guidelines for generating FastAPI routers, Pydantic schemas, and SQLAlchemy models.
---

# Skill: FastAPI CRUD Generator

When writing Python code for a new module based on a spec, you MUST follow these syntax rules:

1. **SQLAlchemy Models:** Always inherit from a declarative base. Use `UUID(as_uuid=True)` for all primary keys (`id`) and foreign keys. 
2. **Pydantic Schemas:** Always create `Base`, `Create`, `Update`, and `Response` schemas. The `Response` schema MUST include `model_config = ConfigDict(from_attributes=True)`.
3. **Routing:** Use `APIRouter(prefix="/<module_slug>", tags=["<Module Name>"])`.
4. **Session & Security:** Inject the database session into every endpoint using `Depends(get_db)`. You MUST also inject the current user/tenant context to enforce Row-Level Security (RLS).
5. **docstatus State Machine:** If the spec includes "DocStatus: Yes", you must implement endpoints for state transitions (e.g., `POST /{id}/submit` to move from 0 to 1).
6. **Pagination:** For `GET` list endpoints, always implement limit/offset pagination and return the data in a standardized paginated response schema.
7. **Error Handling:** Use standard FastAPI `HTTPException` (e.g., 404 for not found, 400 for validation errors) inside `try-except` blocks.