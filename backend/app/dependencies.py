from fastapi import Request, HTTPException
from jose import JWTError, jwt
from uuid import UUID
import os

async def get_tenant_id(request: Request) -> UUID:
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid Authorization header")
    token = auth_header.split(" ")[1]
    try:
        # Use HS256 as specified in the PRD/Tasks
        payload = jwt.decode(token, os.getenv("JWT_SECRET_KEY"), algorithms=["HS256"])
        tenant_id = payload.get("tenant_id")
        if not tenant_id:
            raise HTTPException(status_code=401, detail="tenant_id missing from token payload")
        return UUID(tenant_id)
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

from app.schemas.user_context import UserContext

async def get_current_user(request: Request) -> UserContext:
    """
    Extracts the full authenticated user context from the JWT.
    Returns a typed UserContext with role, employee_id, and company_id.

    Use this dependency in endpoints that need to know WHO is acting,
    not just which tenant the request belongs to.

    Raises 401 if token is missing, invalid, or missing required fields.
    """
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail="Missing or invalid Authorization header"
        )
    token = auth_header.split(" ")[1]
    try:
        payload = jwt.decode(
            token,
            os.getenv("JWT_SECRET_KEY"),
            algorithms=["HS256"]
        )

        tenant_id = payload.get("tenant_id")
        user_id = payload.get("user_id")
        role = payload.get("role")

        if not tenant_id:
            raise HTTPException(status_code=401,
                detail="tenant_id missing from token payload")
        if not user_id:
            raise HTTPException(status_code=401,
                detail="user_id missing from token payload")
        if not role:
            raise HTTPException(status_code=401,
                detail="role missing from token payload")

        employee_id = payload.get("employee_id")
        company_id = payload.get("company_id")

        # Set ContextVar so SQLAlchemy events can read the user_id
        # for auto-populating created_by / modified_by
        from app.db.database import current_user_id_ctx
        current_user_id_ctx.set(UUID(user_id))

        return UserContext(
            user_id=UUID(user_id),
            tenant_id=UUID(tenant_id),
            role=role,
            employee_id=UUID(employee_id) if employee_id else None,
            company_id=UUID(company_id) if company_id else None,
        )

    except JWTError:
        raise HTTPException(status_code=401,
            detail="Invalid or expired token")
