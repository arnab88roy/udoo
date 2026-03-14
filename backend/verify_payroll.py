import httpx
import asyncio
from jose import jwt
from dotenv import load_dotenv
import os
import uuid
from datetime import date, timedelta

load_dotenv()

BASE_URL = "http://127.0.0.1:8000/api"
SECRET_KEY = os.getenv("JWT_SECRET_KEY")
TENANT_ID = "3fa85f64-5717-4562-b3fc-2c963f66afa6"

def get_token():
    payload = {"sub": "test_user", "tenant_id": TENANT_ID}
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")

async def verify_payroll():
    token = get_token()
    headers = {"Authorization": f"Bearer {token}"}
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        print("1. Creating Test Company...")
        company_data = {
            "company_name": f"Payroll Test Co {uuid.uuid4().hex[:4]}",
            "company_code": f"PTC{uuid.uuid4().hex[:3]}",
            "abbr": f"PTC{uuid.uuid4().hex[:2]}",
            "is_active": True
        }
        res = await client.post(f"{BASE_URL}/core-masters/companies/", json=company_data, headers=headers)
        if res.status_code != 201:
            print(f"Failed to create company: {res.text}")
            return
        company = res.json()
        company_id = company["id"]
        print(f"   Success: {company_id}")

        print("2. Creating Compliance Settings...")
        compliance_data = {
            "company_id": company_id,
            "pf_applicable": True,
            "esi_applicable": True,
            "pt_applicable": True,
            "tds_applicable": True,
            "pf_wage_ceiling": 15000,
            "esi_gross_ceiling": 21000
        }
        res = await client.post(f"{BASE_URL}/compliance-settings/", json=compliance_data, headers=headers)
        assert res.status_code == 201
        print("   Success")

        print("2b. Creating PT Slabs for Maharashtra...")
        pt_slabs = [
            {"state_code": "MH", "min_salary": 0, "max_salary": 7499,
             "pt_amount": 0, "is_february": False, "effective_from": "2024-01-01"},
            {"state_code": "MH", "min_salary": 7500, "max_salary": 9999,
             "pt_amount": 175, "is_february": False, "effective_from": "2024-01-01"},
            {"state_code": "MH", "min_salary": 10000, "max_salary": None,
             "pt_amount": 200, "is_february": False, "effective_from": "2024-01-01"},
            {"state_code": "MH", "min_salary": 10000, "max_salary": None,
             "pt_amount": 300, "is_february": True, "effective_from": "2024-01-01"},
        ]
        for slab in pt_slabs:
            res = await client.post(f"{BASE_URL}/pt-slabs/", json=slab, headers=headers)
            assert res.status_code == 201, f"PT slab failed: {res.text}"
        print("   Success: 4 PT slabs created")

        print("3. Fetching Components (Basic & HRA)...")
        res = await client.get(f"{BASE_URL}/salary-components/", headers=headers)
        components = res.json()
        basic_comp = next(c for c in components if c["component_name"] == "Basic")
        hra_comp = next(c for c in components if c["component_name"] == "House Rent Allowance")

        print("4. Creating Salary Structure...")
        structure_data = {
            "structure_name": "Standard Sal Structure",
            "company_id": company_id,
            "is_active": True,
            "components": [
                {"salary_component_id": basic_comp["id"], "calculation_type": "Fixed", "value": 30000, "order_index": 1},
                {"salary_component_id": hra_comp["id"], "calculation_type": "Percentage of Basic", "value": 50, "order_index": 2}
            ]
        }
        res = await client.post(f"{BASE_URL}/salary-structures/", json=structure_data, headers=headers)
        assert res.status_code == 201
        structure = res.json()
        print("   Success")

        print("5a. Creating Gender...")
        gender_data = {"name": f"Male {uuid.uuid4().hex[:4]}"}
        res = await client.post(f"{BASE_URL}/core-masters/genders/", json=gender_data, headers=headers)
        if res.status_code != 201:
            print(f"Failed to create gender: {res.text}")
            return
        gender = res.json()
        gender_id = gender["id"]

        print("5b. Creating Employee...")
        employee_data = {
            "first_name": "Test",
            "last_name": "Payroll",
            "employee_id": f"EMP{uuid.uuid4().hex[:4]}",
            "company_id": company_id,
            "gender_id": gender_id,
            "date_of_birth": "1990-01-01",
            "date_of_joining": "2024-01-01",
            "status": "Active"
        }
        res = await client.post(f"{BASE_URL}/employees/", json=employee_data, headers=headers)
        if res.status_code not in [200, 201]:
            print(f"Failed to create employee: {res.text}")
            return
        employee = res.json()
        employee_id = employee["id"]
        print(f"   Success: {employee_id}")

        print("5c. Linking salary structure to employee...")
        res = await client.patch(
            f"{BASE_URL}/employees/{employee_id}",
            json={"salary_structure_id": structure["id"]},
            headers=headers
        )
        if res.status_code not in [200, 201]:
            print(f"   Warning: Could not link structure to employee: {res.text}")
        else:
            print("   Success")

        print("6. Creating Attendance (Present for 5 days)...")
        for i in range(1, 6):
            atten_data = {
                "employee_id": employee_id,
                "company_id": company_id,
                "attendance_date": f"2024-03-{i:02d}",
                "status": "Present",
                "docstatus": 1
            }
            res = await client.post(f"{BASE_URL}/attendance/", json=atten_data, headers=headers)
            if res.status_code not in [200, 201]:
                print(f"   Failed to create attendance day {i}: {res.text}")
        print("   Success")
        
        print("7. Triggering Bulk Generate for March 2024...")
        bulk_data = {
            "company_id": company_id,
            "payroll_month": 3,
            "payroll_year": 2024,
            "working_days": 31
        }
        res = await client.post(f"{BASE_URL}/salary-slips/bulk-generate", json=bulk_data, headers=headers)
        if res.status_code != 200:
            print(f"   Failed to trigger bulk generate: {res.text}")
            return
        print(f"   Success: {res.json()['message']}")

        print("8. Polling for Salary Slip creation (max 20s)...")
        slip = None
        for _ in range(10):
            await asyncio.sleep(2)
            res = await client.get(f"{BASE_URL}/salary-slips/?employee_id={employee_id}&payroll_month=3&payroll_year=2024", headers=headers)
            slips = res.json()
            if len(slips) > 0:
                slip = slips[0]
                break
        
        if slip:
            print(f"   SUCCESS: Slip created! Gross: {slip['gross_earnings']}, Net: {slip['net_pay']}")
            
            # Mathematical verification
            calculated_net = round(
                float(slip["gross_earnings"]) - float(slip["total_deductions"]), 2
            )
            assert float(slip["net_pay"]) == calculated_net, (
                f"NET PAY MISMATCH: slip shows {slip['net_pay']} "
                f"but gross-deductions = {calculated_net}"
            )
            print(f"   MATH VERIFIED: {slip['gross_earnings']} - "
                  f"{slip['total_deductions']} = {slip['net_pay']} ✓")

            print("9. Testing Submission flow...")
            res = await client.post(f"{BASE_URL}/salary-slips/{slip['id']}/submit", headers=headers)
            assert res.status_code == 200
            assert res.json()["docstatus"] == 1
            print("    Success: Slip submitted")
            
            print("10. Testing Cancellation flow...")
            res = await client.post(f"{BASE_URL}/salary-slips/{slip['id']}/cancel", headers=headers)
            assert res.status_code == 200
            assert res.json()["docstatus"] == 2
            print("    Success: Slip cancelled")
        else:
            print("   FAILURE: Slip not found after polling.")

if __name__ == "__main__":
    asyncio.run(verify_payroll())
