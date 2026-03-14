import httpx
import asyncio
from jose import jwt
from dotenv import load_dotenv
import os

load_dotenv()

BASE_URL = "http://127.0.0.1:8000/api"
SECRET_KEY = os.getenv("JWT_SECRET_KEY")
TENANT_ID = "3fa85f64-5717-4562-b3fc-2c963f66afa6"

def get_token():
    payload = {"sub": "test_user", "tenant_id": TENANT_ID}
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")

async def seed_payroll():
    token = get_token()
    headers = {"Authorization": f"Bearer {token}"}
    
    components = [
        {"component_name": "Basic", "component_type": "Earning", "is_statutory": False, "is_taxable": True, "description": "Base salary"},
        {"component_name": "House Rent Allowance", "component_type": "Earning", "is_statutory": False, "is_taxable": True, "description": "HRA"},
        {"component_name": "Provident Fund - Employee", "component_type": "Deduction", "is_statutory": True, "is_taxable": False, "description": "Employee PF contribution"},
        {"component_name": "Provident Fund - Employer", "component_type": "Deduction", "is_statutory": True, "is_taxable": False, "description": "Employer PF contribution"},
        {"component_name": "ESI - Employee", "component_type": "Deduction", "is_statutory": True, "is_taxable": False, "description": "Employee ESI contribution"},
        {"component_name": "ESI - Employer", "component_type": "Deduction", "is_statutory": True, "is_taxable": False, "description": "Employer ESI contribution"},
        {"component_name": "Professional Tax", "component_type": "Deduction", "is_statutory": True, "is_taxable": False, "description": "State PT"},
        {"component_name": "TDS", "component_type": "Deduction", "is_statutory": True, "is_taxable": False, "description": "Income Tax deduction"}
    ]
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        # Seed Components
        for comp in components:
            print(f"Seeding component: {comp['component_name']}")
            res = await client.post(f"{BASE_URL}/salary-components/", json=comp, headers=headers)
            if res.status_code == 201:
                print("  Success")
            elif res.status_code == 400 and "already exists" in res.text:
                print("  Already exists")
            else:
                print(f"  Failed: {res.status_code} - {res.text}")
        
        # Seed PT Slabs (Maharashtra MH)
        print("Seeding PT Slabs for MH...")
        pt_slabs = [
            {"state_code": "MH", "min_salary": 0, "max_salary": 7500, "pt_amount": 0, "is_february": False, "effective_from": "2024-04-01"},
            {"state_code": "MH", "min_salary": 7501, "max_salary": 10000, "pt_amount": 175, "is_february": False, "effective_from": "2024-04-01"},
            {"state_code": "MH", "min_salary": 10001, "max_salary": 9999999, "pt_amount": 200, "is_february": False, "effective_from": "2024-04-01"},
            {"state_code": "MH", "min_salary": 10001, "max_salary": 9999999, "pt_amount": 2500, "is_february": True, "effective_from": "2024-04-01"}
        ]
        for slab in pt_slabs:
            res = await client.post(f"{BASE_URL}/pt-slabs/", json=slab, headers=headers)
            if res.status_code == 201:
                print(f"  PT Slab {slab['min_salary']}-{slab['max_salary']} success")
            else:
                print(f"  PT Slab failed: {res.status_code} - {res.text}")

if __name__ == "__main__":
    asyncio.run(seed_payroll())
