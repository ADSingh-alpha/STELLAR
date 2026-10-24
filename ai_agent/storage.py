"""
Stellar AI - Cloud Storage & Direct Upload Manager
Resolves the 'Heavy File Upload' bottleneck by enabling:
1. Direct presigned URL uploads to AWS S3 / MinIO (bypassing application servers entirely).
2. Direct high-throughput streaming uploads to the FastAPI microservice raster store,
   completely bypassing the Express Node.js API Gateway event loop.
"""

import os
import uuid
import time
from pathlib import Path
from typing import Dict, Any, Optional

try:
    import boto3
    from botocore.exceptions import ClientError
    BOTO3_AVAILABLE = True
except ImportError:
    BOTO3_AVAILABLE = False
    boto3 = None

UPLOAD_DIR = Path(__file__).resolve().parent / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# S3 / MinIO Configuration
S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME", "")
S3_REGION = os.getenv("AWS_REGION", "us-east-1")
S3_ENDPOINT_URL = os.getenv("S3_ENDPOINT_URL")  # Useful for MinIO or localstack
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")


def is_s3_configured() -> bool:
    """Return True if AWS S3 or MinIO credentials are configured."""
    return bool(BOTO3_AVAILABLE and S3_BUCKET_NAME and AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY)


def get_s3_client():
    """Create and return configured boto3 S3 client."""
    if not is_s3_configured():
        return None
    return boto3.client(
        "s3",
        region_name=S3_REGION,
        endpoint_url=S3_ENDPOINT_URL,
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    )


def generate_presigned_upload_url(
    filename: str,
    file_type: str = "image/tiff",
    expires_in_seconds: int = 3600
) -> Dict[str, Any]:
    """
    Generate a presigned upload URL for direct client-to-storage uploads.
    
    If S3 / MinIO is configured:
      Returns an S3 Presigned PUT URL. The client sends a direct PUT request to S3/MinIO.
      No satellite binary passes through either Express or FastAPI.
      
    If S3 is not configured (local dev mode):
      Returns a direct high-throughput streaming URL to FastAPI's raster store,
      bypassing Express.
    """
    clean_filename = Path(filename).name
    unique_key = f"rasters/{uuid.uuid4().hex[:8]}_{clean_filename}"

    if is_s3_configured():
        s3 = get_s3_client()
        try:
            presigned_url = s3.generate_presigned_url(
                ClientMethod="put_object",
                Params={
                    "Bucket": S3_BUCKET_NAME,
                    "Key": unique_key,
                    "ContentType": file_type,
                },
                ExpiresIn=expires_in_seconds,
            )
            return {
                "storage_backend": "s3",
                "upload_url": presigned_url,
                "method": "PUT",
                "storage_key": unique_key,
                "s3_uri": f"s3://{S3_BUCKET_NAME}/{unique_key}",
                "public_url": f"https://{S3_BUCKET_NAME}.s3.{S3_REGION}.amazonaws.com/{unique_key}",
                "expires_in": expires_in_seconds,
                "headers": {"Content-Type": file_type},
            }
        except Exception as e:
            # Fall back to direct FastAPI stream if S3 error occurs
            pass

    # Direct streaming upload to FastAPI raster store (bypassing Express)
    upload_id = str(uuid.uuid4())
    destination_filename = f"{upload_id[:8]}_{clean_filename}"
    return {
        "storage_backend": "fastapi_direct_stream",
        "upload_url": f"/api/v1/upload/direct?upload_id={upload_id}&filename={clean_filename}",
        "method": "POST",
        "upload_id": upload_id,
        "storage_key": destination_filename,
        "destination_filename": destination_filename,
        "expires_in": expires_in_seconds,
        "headers": {"Content-Type": file_type},
    }
