import asyncio
from httpx import AsyncClient, ASGITransport
import uuid
import sys
import os

# Ensure the app module can be found
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'app')))

from app.main import app, get_tenant_id
from app.db.database import get_db
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.pool import NullPool

# Mock tenant
TEST_TENANT_ID = uuid.uuid4()
def mock_get_tenant_id(): return TEST_TENANT_ID
app.dependency_overrides[get_tenant_id] = mock_get_tenant_id

# Override DB with correct parameters
test_engine = create_async_engine(
    os.getenv("DATABASE_URL"), 
    poolclass=NullPool,
    connect_args={
        "server_settings": {"application_name": "udoo_erp_test"},
        "prepared_statement_cache_size": 0,
        "statement_cache_size": 0
    }
)
TestingSessionLocal = async_sessionmaker(test_engine, class_=AsyncSession, expire_on_commit=False)
async def override_get_db():
    async with TestingSessionLocal() as session: yield session
app.dependency_overrides[get_db] = override_get_db

async def main():
    transport = ASGITransport(app=app)
    headers = {
        "Authorization": "Bearer test-token",
        "X-Tenant-ID": str(TEST_TENANT_ID),
        "Content-Type": "application/json"
    }
    
    # 1. Create dependencies
    async with AsyncClient(transport=transport, base_url="http://test", headers=headers) as client:
        abbr = str(uuid.uuid4())[:4].upper()
        comp = await client.post("/api/core-masters/companies/", json={"company_name": f"Test Company {abbr}", "abbr": abbr})
        company_id = comp.json()["id"]
        
        gen_name = "G-" + str(uuid.uuid4())[:4]
        gen = await client.post("/api/core-masters/genders/", json={"name": gen_name})
        gender_id = gen.json()["id"]

        user = await client.post("/api/core-masters/users/", json={"email": f"test{uuid.uuid4()}@test.com", "first_name": "Test", "send_welcome_email": False})
        user_id = user.json()["id"]
        
        # 2. Create employee
        employee_data = {
            "naming_series": "HR-EMP-",
            "first_name": "John",
            "last_name": "Doe",
            "gender_id": gender_id,
            "date_of_birth": "1990-01-01",
            "company_id": company_id,
            "date_of_joining": "2023-01-01",
            "education": [{"school_univ": "MIT", "qualification": "BSc"}],
            "external_work_history": [{"company_name": "Google", "designation": "Engineer"}],
            "user_id": user_id
        }
        
        response = await client.post("/api/employees/", json=employee_data)
        print(f"Status: {response.status_code}")
        
        if response.status_code != 201:
            print("ERROR DETAILS:")
            print(response.json())

if __name__ == "__main__":
    asyncio.run(main())
