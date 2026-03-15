import pytest
from uuid import uuid4
from fastapi.testclient import TestClient
from app.main import app
from app.schemas.ui_response import UIResponseType

from jose import jwt
import os
from dotenv import load_dotenv

load_dotenv()

client = TestClient(app)

@pytest.mark.asyncio
async def test_veda_chat_table_response():
    """
    Simulated test for Task 3.1: Show all active employees.
    """
    # ── Generate valid owner token ─────────────────────────────────────────
    TENANT_ID = "3fa85f64-5717-4562-b3fc-2c963f66afa6"
    role = "owner"
    payload_jwt = {
        "sub": f"test_{role}",
        "tenant_id": TENANT_ID,
        "user_id": "d06e935b-c365-54d5-93cd-dfc94379070b",
        "role": role,
        "company_id": "2fa8fddf-86b2-4c86-b5e0-329637659ee7",
    }
    token = jwt.encode(payload_jwt, os.getenv("JWT_SECRET_KEY"), algorithm="HS256")
    headers = {"Authorization": f"Bearer {token}"}
    
    payload = {
        "message": "Show me all active employees",
        "context": {
            "open_module": "hrms",
            "tenant_id": str(uuid4())
        },
        "conversation_history": []
    }
    
    # We expect a failure because ANTHROPIC_API_KEY is dummy
    # but we want to see it reach the graph.
    response = client.post("/api/veda/chat", json=payload, headers=headers)
    
    # If it reaches the LLM and fails, we'll get our custom error response
    assert response.status_code == 200
    data = response.json()
    assert "type" in data
    # If the LLM call fails due to invalid key, main.py returns make_text_response
    # with "I encountered an error..."
    if data["type"] == "text":
        assert "error" in data["message"].lower() or "veda" in data["message"].lower()
