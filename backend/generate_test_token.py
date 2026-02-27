import base64
import json
import hmac
import hashlib

def create_jwt(payload, secret):
    header = {"alg": "HS256", "typ": "JWT"}
    encoded_header = base64.urlsafe_b64encode(json.dumps(header).encode()).decode().rstrip("=")
    encoded_payload = base64.urlsafe_b64encode(json.dumps(payload).encode()).decode().rstrip("=")
    signature = hmac.new(secret.encode(), f"{encoded_header}.{encoded_payload}".encode(), hashlib.sha256).digest()
    encoded_signature = base64.urlsafe_b64encode(signature).decode().rstrip("=")
    return f"{encoded_header}.{encoded_payload}.{encoded_signature}"

tenant_id = "3fa85f64-5717-4562-b3fc-2c963f66afa6"
token = create_jwt({"sub": "test_user", "tenant_id": tenant_id}, "dummy_secret_key")

print("\n" + "="*50)
print("TEST JWT TOKEN (Copy the string below):")
print("="*50)
print(f"{token}")
print("="*50 + "\n")
