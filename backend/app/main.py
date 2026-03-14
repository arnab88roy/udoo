import logging
from fastapi import FastAPI, Depends, Request, HTTPException
from fastapi.responses import JSONResponse
from uuid import UUID

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

    # 3. Token exists and has Bearer prefix — proceed.
    # Actual tenant_id extraction happens in get_tenant_id() via Depends().
    # Do NOT read X-Tenant-ID header here — that was the old insecure pattern.
    return await call_next(request)

from app.dependencies import get_tenant_id
from app.schemas.ui_response import UIResponse, VEDARequest, make_text_response

@app.get("/")
async def root():

    return {"message": "AI-Native ERP Engine API running securely."}

@app.get("/api/health")
async def health_check():
    return {"status": "ok"}

from app.modules.core_masters.router import router as core_masters_router
from app.modules.org_masters.router import router as org_masters_router
from app.modules.hr_masters.routers import (
    router as hr_masters_router,
    employee_router as hr_employee_router,
    leave_type_router,
    leave_application_router,
    checkin_router,
    attendance_router,
    attendance_request_router
)
from app.modules.payroll.router import (
    compliance_router,
    pt_slab_router,
    salary_component_router,
    salary_structure_router,
    salary_slip_router
)
from app.modules.finance.router import (
    exchange_rate_router,
    tax_template_router,
    client_router,
    quote_router,
    proforma_router,
    invoice_router,
    payment_router,
    recurring_router,
    salary_slip_html_router,
    finance_reports_router
)

app.include_router(core_masters_router, prefix="/api")
app.include_router(org_masters_router, prefix="/api")
app.include_router(hr_masters_router, prefix="/api")
app.include_router(hr_employee_router, prefix="/api")
app.include_router(leave_type_router, prefix="/api")
app.include_router(leave_application_router, prefix="/api")
app.include_router(checkin_router, prefix="/api")
app.include_router(attendance_router, prefix="/api")
app.include_router(attendance_request_router, prefix="/api")

# Payroll Routers
app.include_router(compliance_router, prefix="/api")
app.include_router(pt_slab_router, prefix="/api")
app.include_router(salary_component_router, prefix="/api")
app.include_router(salary_structure_router, prefix="/api")
app.include_router(salary_slip_router, prefix="/api")

# Finance Routers
app.include_router(exchange_rate_router, prefix="/api")
app.include_router(tax_template_router, prefix="/api")
app.include_router(client_router, prefix="/api")
app.include_router(quote_router, prefix="/api")
app.include_router(proforma_router, prefix="/api")
app.include_router(invoice_router, prefix="/api")
app.include_router(payment_router, prefix="/api")
app.include_router(recurring_router, prefix="/api")
app.include_router(salary_slip_html_router, prefix="/api")
app.include_router(finance_reports_router, prefix="/api")

from app.utils.veda_context import sanitise_request_context, describe_context

@app.post("/api/veda/chat", response_model=UIResponse)
async def veda_chat(
    request: VEDARequest,
    tenant_id: UUID = Depends(get_tenant_id)
):
    """
    VEDA chat endpoint. Accepts a natural language message and
    returns a typed UIResponse for the frontend to render.

    Security: tenant_id from JWT always overrides client-supplied value.
    Context: Active record context is passed automatically by the frontend.
    Stub: Returns TEXT response until LangGraph is wired in Task 3.1.
    """
    # SECURITY: Always sanitise context — JWT tenant_id overwrites client value
    safe_context = sanitise_request_context(request.context, tenant_id)

    # STUB: Real LangGraph routing implemented in Task 3.1
    # Returns context description so frontend and tests can verify
    # context is flowing correctly before LangGraph is wired.
    context_description = describe_context(safe_context)

    return make_text_response(
        message=(
            f"VEDA received: '{request.message}'. "
            f"Context: {context_description} "
            f"LangGraph routing will be wired in Task 3.1."
        ),
        context=safe_context,
        hints=[
            "Show all active employees",
            "Run payroll for this month",
            "Show pending leave approvals"
        ]
    )

@app.get("/api/me")
async def get_current_tenant_info(tenant_id: UUID = Depends(get_tenant_id)):
    """
    Example protected endpoint that relies on the Dependency Injection function
    to isolate requests using PostgreSQL RLS (tenant_id).
    """
    return {
        "tenant_id": tenant_id,
        "message": "Tenant boundaries correctly isolated."
    }
