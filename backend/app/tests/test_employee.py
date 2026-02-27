import pytest
from httpx import AsyncClient
import uuid

pytestmark = pytest.mark.asyncio

async def test_create_employee_with_children(client: AsyncClient):
    test_id = str(uuid.uuid4())[:8]

    # 1. Create a Company
    company_payload = {
        "company_name": f"Test Company {test_id}",
        "abbr": f"TC{test_id}",
        "default_currency": "USD",
        "country": "Testland"
    }
    comp_res = await client.post("/api/core-masters/companies/", json=company_payload)
    if comp_res.status_code == 404: 
        company_id = str(uuid.uuid4())
    else:
        assert comp_res.status_code in [200, 201], f"Company creation failed: {comp_res.text}"
        company_id = comp_res.json()["id"]

    # 2. Create Gender
    gender_payload = {
        "name": f"Test Gender {test_id}"
    }
    gen_res = await client.post("/api/core-masters/genders/", json=gender_payload)
    assert gen_res.status_code in [200, 201], f"Failed to POST gender: {gen_res.text}"
    gender_id = gen_res.json()["id"]

    # 3. Create Employee Payload
    payload = {
        "first_name": f"John {test_id}",
        "last_name": "Doe",
        "gender_id": gender_id,
        "date_of_birth": "1990-01-01",
        "company_id": company_id,
        "date_of_joining": "2026-01-01",
        "salary_mode": "Bank",
        "education": [
            {
                "school_univ": "Test University",
                "qualification": "BSc Computer Science",
                "level": "Graduate",
                "year_of_passing": 2012,
                "class_per": "First Class"
            }
        ],
        "external_work_history": [
            {
                "company_name": "Old Corp",
                "designation": "Software Engineer",
                "salary": 100000.0,
                "total_experience": "4 years"
            }
        ],
        "internal_work_history": []
    }

    response = await client.post("/api/employees/", json=payload)
    assert response.status_code == 200, f"Employee creation failed: {response.text}"
    
    data = response.json()
    assert data["first_name"] == f"John {test_id}"
    assert data["employee_name"] == f"John {test_id} Doe"
    assert data["tenant_id"] is not None
    
    assert len(data["education"]) == 1
    assert data["education"][0]["school_univ"] == "Test University"
    
    assert len(data["external_work_history"]) == 1
    assert data["external_work_history"][0]["company_name"] == "Old Corp"

