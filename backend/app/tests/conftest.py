import os
from dotenv import load_dotenv
import uuid
import pytest
import pytest_asyncio
import uvloop
import asyncio
from httpx import AsyncClient, ASGITransport

# Load environment variables from .env
load_dotenv()

from app.main import app, get_tenant_id
from app.db.database import get_db
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.pool import NullPool

# Mocked tenant UUID
TEST_TENANT_ID = uuid.uuid4()

def mock_get_tenant_id():
    return TEST_TENANT_ID

app.dependency_overrides[get_tenant_id] = mock_get_tenant_id

# Override Database Engine with NullPool to avoid Pytest Asyncio Event Loop Deadlocks
test_engine = create_async_engine(
    os.getenv("DATABASE_URL"), 
    poolclass=NullPool,
    connect_args={
        "server_settings": {
            "application_name": "udoo_erp_test",
        },
        "prepared_statement_cache_size": 0,
        "statement_cache_size": 0
    }
)
TestingSessionLocal = async_sessionmaker(test_engine, class_=AsyncSession, expire_on_commit=False)

async def override_get_db():
    async with TestingSessionLocal() as session:
        yield session

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(scope="session")
def event_loop():
    """Forces pytest-asyncio to use uvloop for the entire session to prevent MacOS anyio deadlocks"""
    loop = uvloop.new_event_loop()
    asyncio.set_event_loop(loop)
    yield loop
    loop.close()

@pytest_asyncio.fixture()
async def client():
    transport = ASGITransport(app=app)
    headers = {
        "Authorization": "Bearer test-token",
        "X-Tenant-ID": str(TEST_TENANT_ID)
    }
    async with AsyncClient(transport=transport, base_url="http://test", headers=headers) as c:
        yield c
