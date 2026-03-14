import asyncio
from httpx import AsyncClient
import uuid

# The test tenant we set in generate_test_token.py
TENANT_ID = "3fa85f64-5717-4562-b3fc-2c963f66afa6"
# The token generated from that tenant
TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0X3VzZXIiLCJ0ZW5hbnRfaWQiOiIzZmE4NWY2NC01NzE3LTQ1NjItYjNmYy0yYzk2M2Y2NmFmYTYifQ.1DahwHwgMm0jXLywdsFXk9rH9a7vdNIq6XGq2FDcR8g"

BASE_URL = "http://127.0.0.1:8000/api"

async def main():
    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json"
    }
    
    async with AsyncClient(base_url=BASE_URL, headers=headers, timeout=60.0) as client:
        print("Seeding data for test tenant...")
        
        # 1. Create Company
        abbr = str(uuid.uuid4())[:4].upper()
        comp_res = await client.post("/core-masters/companies/", json={"company_name": f"Test Company {abbr}", "abbr": abbr})
        if comp_res.status_code != 201:
            print(f"Failed to create Company: {comp_res.text}")
            return
        company_id = comp_res.json()["id"]
        print(f"Created Company: {company_id}")

        # 2. Create Gender (Required for Employee)
        gen_name = "Seed G-" + str(uuid.uuid4())[:4]
        gen_res = await client.post("/core-masters/genders/", json={"name": gen_name})
        if gen_res.status_code != 201:
            print(f"Failed to create Gender: {gen_res.text}")
            return
        gender_id = gen_res.json()["id"]
        print(f"Created Gender: {gender_id}")

        # 3. Create Department
        dept_name = "Seed D-" + str(uuid.uuid4())[:4]
        dept_res = await client.post("/departments/", json={"department_name": dept_name, "company": company_id})
        if dept_res.status_code != 201:
            print(f"Failed to create Department: {dept_res.text}")
            return
        department_id = dept_res.json()["id"]
        print(f"Created Department: {department_id}")

        # 4. Create Employee
        emp_data = {
            "first_name": "Test",
            "last_name": "Employee",
            "gender_id": gender_id,
            "date_of_birth": "1990-01-01",
            "company_id": company_id,
            "department_id": department_id,
            "date_of_joining": "2023-01-01"
        }
        emp_res = await client.post("/employees/", json=emp_data)
        if emp_res.status_code not in (200, 201):
            print(f"Failed to create Employee: {emp_res.text}")
            return
        employee_id = emp_res.json()["id"]
        
        print("\n" + "="*50)
        print("SEEDING COMPLETE. USE THESE IDs FOR TESTING:")
        print("="*50)
        print(f"Employee ID:   {employee_id}")
        print(f"Company ID:    {company_id}")
        print(f"Department ID: {department_id}")
        print("="*50 + "\n")

if __name__ == "__main__":
    asyncio.run(main())
