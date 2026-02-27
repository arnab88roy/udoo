import logging
from fastapi import FastAPI, Depends, Request, HTTPException
from fastapi.responses import JSONResponse
from contextvars import ContextVar

# Setup basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="AI-Native ERP Meta-Engine", version="0.1.0")

from fastapi.openapi.utils import get_openapi

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="AI-Native ERP Meta-Engine",
        version="0.1.0",
        routes=app.routes,
    )
    # Add BearerAuth to components
    if "components" not in openapi_schema:
        openapi_schema["components"] = {}
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
        }
    }
    # Apply security globally
    for path in openapi_schema.get("paths", {}).values():
        for method in path.values():
            method.setdefault("security", [])
            method["security"].append({"BearerAuth": []})
            
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

# Placeholder ContextVar for the Tenant ID to support Row-Level Security
# For async scenarios, passing it explicitly in route handlers is typically better,
# but ContextVars allow low-level SQLAlchemy hooks to access the tenant transparently.
_tenant_id_ctx: ContextVar[str] = ContextVar("tenant_id", default="")

@app.middleware("http")
async def jwt_authentication_middleware(request: Request, call_next):
    """
    Placeholder JWT Authentication Middleware.
    Extracts tenant context and validates authorization header.
    """
    # 1. Skip auth for public paths (e.g., OpenAPI docs)
    if request.url.path in ["/docs", "/openapi.json", "/"]:
        return await call_next(request)

    # 2. Extract JWT token (Placeholder logic)
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return JSONResponse(status_code=401, content={"detail": "Missing JWT Token"})

    # 3. Extract Tenant ID (Simulating JWT decoding boundary)
    # In a real setup, `tenant_id` comes from the decoded token payload.
    tenant_id = request.headers.get("X-Tenant-ID", "3fa85f64-5717-4562-b3fc-2c963f66afa6")
    
    # 4. Set Tenant ID in ContextVar for potential low-level hooks
    token = _tenant_id_ctx.set(tenant_id)
    
    # 5. Proceed with the request
    try:
        response = await call_next(request)
        return response
    finally:
        _tenant_id_ctx.reset(token)

from app.dependencies import get_tenant_id

@app.get("/")
async def root():

    return {"message": "AI-Native ERP Engine API running securely."}

@app.get("/api/health")
async def health_check():
    return {"status": "ok"}

from app.modules.core_masters.router import router as core_masters_router
from app.modules.org_masters.router import router as org_masters_router
from app.modules.hr_masters.router import router as hr_masters_router, employee_router as hr_employee_router, leave_type_router, leave_application_router

app.include_router(core_masters_router, prefix="/api")
app.include_router(org_masters_router, prefix="/api")
app.include_router(hr_masters_router, prefix="/api")
app.include_router(hr_employee_router, prefix="/api")
app.include_router(leave_type_router, prefix="/api")
app.include_router(leave_application_router, prefix="/api")

@app.get("/api/me")
async def get_current_tenant_info(tenant_id: str = Depends(get_tenant_id)):
    """
    Example protected endpoint that relies on the Dependency Injection function
    to isolate requests using PostgreSQL RLS (tenant_id).
    """
    return {
        "tenant_id": tenant_id,
        "message": "Tenant boundaries correctly isolated."
    }
