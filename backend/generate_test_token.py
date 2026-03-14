from jose import jwt
from dotenv import load_dotenv
import os
import uuid

load_dotenv()

TENANT_ID = "3fa85f64-5717-4562-b3fc-2c963f66afa6"
TEST_EMPLOYEE_ID = "66ddb47a-3f4d-4275-9e3d-f06cd420f26d"
TEST_COMPANY_ID = "2fa8fddf-86b2-4c86-b5e0-329637659ee7"

ROLES = ["owner", "hr_manager", "finance_manager", "manager", "employee", "auditor"]

print("Generate test JWT token")
print("=" * 40)
print("Available roles:")
for i, r in enumerate(ROLES, 1):
    print(f"  {i}. {r}")

choice = input("\nSelect role number [1 for owner]: ").strip() or "1"
try:
    role = ROLES[int(choice) - 1]
except (ValueError, IndexError):
    role = "owner"

user_id = str(uuid.uuid5(uuid.UUID(TENANT_ID), role))

payload = {
    "sub": f"test_{role}",
    "tenant_id": TENANT_ID,
    "user_id": user_id,
    "role": role,
    "employee_id": TEST_EMPLOYEE_ID if role != "owner" else None,
    "company_id": TEST_COMPANY_ID,
}
payload = {k: v for k, v in payload.items() if v is not None}

token = jwt.encode(payload, os.getenv("JWT_SECRET_KEY"), algorithm="HS256")

print(f"\nRole: {role}")
print(f"User ID: {user_id}")
print("=" * 50)
print("JWT TOKEN:")
print("=" * 50)
print(token)
print("=" * 50)
