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
