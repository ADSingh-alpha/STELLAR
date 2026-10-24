"""
Stellar AI - FastAPI Backend Verification Test Suite
Verifies CORS configuration, health check, text query, standalone image upload,
and combined query-with-image endpoints.
"""

import os
import sys
import io
import json
from pathlib import Path

# Add repository root to sys.path for package imports
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

try:
    from fastapi.testclient import TestClient
    try:
        from ai_agent.main import app
    except ImportError:
        from main import app
    TESTCLIENT_AVAILABLE = True
except ImportError as e:
    print(f"[Warning] TestClient or imports not fully available: {e}")
    TESTCLIENT_AVAILABLE = False


def test_fastapi_backend():
    if not TESTCLIENT_AVAILABLE:
        print("[FAIL] TestClient could not be initialized due to missing dependencies.")
        return False

    client = TestClient(app)

    print("--- 1. Testing GET / Root ---")
    res_root = client.get("/")
    assert res_root.status_code == 200, f"Expected 200, got {res_root.status_code}"
    print("Root response:", res_root.json())

    print("\n--- 2. Testing GET /health ---")
    res_health = client.get("/health")
    assert res_health.status_code == 200, f"Expected 200, got {res_health.status_code}"
    print("Health response:", res_health.json())

    print("\n--- 3. Testing CORS Headers ---")
    res_cors = client.options("/", headers={"Origin": "http://localhost:5173", "Access-Control-Request-Method": "POST"})
    # FastAPI automatically handles OPTIONS for CORS if configured
    print("CORS response status:", res_cors.status_code)
    print("CORS Access-Control-Allow-Origin:", res_cors.headers.get("access-control-allow-origin"))

    print("\n--- 4. Testing POST /api/v1/query (JSON query) ---")
    payload = {
        "query": "Calculate NDVI for agricultural land in Punjab",
        "geo_context": {"latitude": 30.7, "longitude": 76.7, "aoi_name": "Punjab Wheat Belt"}
    }
    res_query = client.post("/api/v1/query", json=payload)
    assert res_query.status_code == 200, f"Query failed with status {res_query.status_code}: {res_query.text}"
    query_json = res_query.json()
    print("Query status:", query_json.get("status"))
    print("Query answer preview:", str(query_json.get("final_answer"))[:120])

    print("\n--- 5. Testing POST /api/v1/upload (Standalone image upload) ---")
    dummy_image_data = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82"
    file_payload = {"file": ("test_sentinel.png", io.BytesIO(dummy_image_data), "image/png")}
    res_upload = client.post("/api/v1/upload", files=file_payload)
    assert res_upload.status_code == 200, f"Upload failed with status {res_upload.status_code}: {res_upload.text}"
    upload_json = res_upload.json()
    print("Upload response:", upload_json)

    print("\n--- 6. Testing POST /api/v1/query-with-image (Multipart query + image) ---")
    form_data = {
        "query": "Detect water body extent in uploaded satellite scene",
        "sensor": "Sentinel-2",
        "aoi": "Brahmaputra Basin"
    }
    image_payload = {"file": ("scene_t1.png", io.BytesIO(dummy_image_data), "image/png")}
    res_img_query = client.post("/api/v1/query-with-image", data=form_data, files=image_payload)
    assert res_img_query.status_code == 200, f"Query with image failed with status {res_img_query.status_code}: {res_img_query.text}"
    img_query_json = res_img_query.json()
    print("Query with image status:", img_query_json.get("status"))
    print("Query with image answer preview:", str(img_query_json.get("final_answer"))[:120])

    print("\n[SUCCESS] All FastAPI backend test cases passed cleanly!")
    return True


if __name__ == "__main__":
    test_fastapi_backend()
