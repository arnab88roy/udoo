import logging
from fastapi import FastAPI, Depends, Request, HTTPException
from fastapi.responses import JSONResponse
from contextvars import ContextVar

# Setup basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="AI-Native ERP Meta-Engine", version="0.1.0")

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
    tenant_id = request.headers.get("X-Tenant-ID", "default_tenant_id")
    
    # 4. Set Tenant ID in ContextVar for potential low-level hooks
    token = _tenant_id_ctx.set(tenant_id)
    
    # 5. Proceed with the request
    try:
        response = await call_next(request)
        return response
    finally:
        _tenant_id_ctx.reset(token)

async def get_tenant_id(request: Request) -> str:
    """
    Dependency Injection function to extract tenant_id for Database RLS.
    In practice, you could pull this from request.state set by middleware,
    or extract it freshly from the validated JWT token.
    """
    # Simply mapping the X-Tenant-ID header as a placeholder for the verified JWT claim
    tenant_id = request.headers.get("X-Tenant-ID", "default_tenant_id")
    return tenant_id

@app.get("/")
async def root():
    return {"message": "AI-Native ERP Engine API running securely."}

@app.get("/api/health")
async def health_check():
    return {"status": "ok"}

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
