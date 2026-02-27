from fastapi import Request

async def get_tenant_id(request: Request) -> str:
    """
    Dependency Injection function to extract tenant_id for Database RLS.
    """
    tenant_id = request.headers.get("X-Tenant-ID", "3fa85f64-5717-4562-b3fc-2c963f66afa6")
    return tenant_id
