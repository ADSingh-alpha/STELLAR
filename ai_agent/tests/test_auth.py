"""
Stellar AI - Authentication Test Suite
Tests password hashing, JWT encoding/decoding, user registration (/signup),
login authentication (/login), and user profile fetching (/me).
"""

import sys
import uuid
from pathlib import Path

# Add repository root to sys.path for package imports
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from fastapi.testclient import TestClient
try:
    from ai_agent.main import app
    from ai_agent.auth import hash_password, verify_password, create_access_token, decode_access_token
except ImportError:
    from main import app
    from auth import hash_password, verify_password, create_access_token, decode_access_token


def test_auth_pipeline():
    client = TestClient(app)

    print("--- 1. Testing Password Hashing & Verification ---")
    password = "SuperSecretPassword123!"
    hashed = hash_password(password)
    assert hashed != password, "Hashed password should not equal plain text"
    assert verify_password(password, hashed) is True, "Password verification failed"
    assert verify_password("WrongPassword", hashed) is False, "Invalid password passed verification unexpectedly"
    print("[PASS] Password hashing and verification working cleanly.")

    print("\n--- 2. Testing JWT Token Encoding & Decoding ---")
    token_data = {"sub": "testuser", "user_id": 999, "email": "testuser@stellar.ai"}
    token = create_access_token(token_data)
    assert isinstance(token, str) and len(token) > 20, "JWT token generation failed"

    decoded = decode_access_token(token)
    assert decoded is not None, "JWT decoding failed"
    assert decoded.get("sub") == "testuser", f"Expected sub 'testuser', got {decoded.get('sub')}"
    assert decoded.get("user_id") == 999, f"Expected user_id 999, got {decoded.get('user_id')}"
    print("[PASS] JWT token generation and decoding working cleanly.")

    print("\n--- 3. Testing POST /signup (User Registration) ---")
    unique_id = str(uuid.uuid4())[:8]
    signup_payload = {
        "email": f"astro_{unique_id}@stellar.ai",
        "username": f"astro_user_{unique_id}",
        "password": "StellarPassword2026!",
        "full_name": "Stellar Analyst"
    }

    res_signup = client.post("/signup", json=signup_payload)
    assert res_signup.status_code == 200, f"Signup failed: {res_signup.status_code} - {res_signup.text}"
    signup_json = res_signup.json()
    assert "access_token" in signup_json, "Missing access_token in signup response"
    assert signup_json["user"]["email"] == signup_payload["email"], "User email mismatch"
    token = signup_json["access_token"]
    print("Signup Response:", signup_json)

    print("\n--- 4. Testing POST /login (User Authentication) ---")
    login_payload = {
        "username_or_email": signup_payload["username"],
        "password": signup_payload["password"]
    }
    res_login = client.post("/login", json=login_payload)
    assert res_login.status_code == 200, f"Login failed: {res_login.status_code} - {res_login.text}"
    login_json = res_login.json()
    assert "access_token" in login_json, "Missing access_token in login response"
    assert login_json["user"]["username"] == signup_payload["username"], "User username mismatch"
    print("Login Response:", login_json)

    print("\n--- 5. Testing GET /api/v1/auth/me (Protected Profile Route) ---")
    headers = {"Authorization": f"Bearer {token}"}
    res_me = client.get("/api/v1/auth/me", headers=headers)
    assert res_me.status_code == 200, f"Me endpoint failed: {res_me.status_code} - {res_me.text}"
    me_json = res_me.json()
    assert me_json["email"] == signup_payload["email"], "Profile email mismatch"
    print("Profile Response:", me_json)

    print("\n[SUCCESS] All Authentication Backend Tests Passed Cleanly!")
    return True


if __name__ == "__main__":
    test_auth_pipeline()
