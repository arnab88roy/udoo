from jose import jwt
from dotenv import load_dotenv
import os

load_dotenv()
tenant_id = "3fa85f64-5717-4562-b3fc-2c963f66afa6"
payload = {"sub": "test_user", "tenant_id": tenant_id}
token = jwt.encode(payload, os.getenv("JWT_SECRET_KEY"), algorithm="HS256")
print(token)
