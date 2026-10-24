"""
Stellar AI - Authentication Module
Provides PostgreSQL User model (with SQLite fallback), password hashing via passlib/bcrypt,
and JWT access token generation and validation.
"""

import os
import jwt
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from pydantic import BaseModel, EmailStr, Field

# ---------------------------------------------------------------------------
# Password Hashing Setup
# ---------------------------------------------------------------------------

try:
    import bcrypt
    if not hasattr(bcrypt, "__about__") and hasattr(bcrypt, "__version__"):
        bcrypt.__about__ = type("about", (), {"__version__": bcrypt.__version__})
    from passlib.context import CryptContext
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    PASSLIB_AVAILABLE = True
except Exception:
    PASSLIB_AVAILABLE = False

import hashlib
import hmac


def hash_password(password: str) -> str:
    """Hash password using passlib/bcrypt with SHA256 HMAC fallback."""
    if PASSLIB_AVAILABLE:
        try:
            return pwd_context.hash(password)
        except Exception:
            pass
    # Fallback secure hash
    salt = "stellar_salt_2026"
    return hmac.new(salt.encode(), password.encode(), hashlib.sha256).hexdigest()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify plain text password against stored hash."""
    if PASSLIB_AVAILABLE and (hashed_password.startswith("$2b$") or hashed_password.startswith("$2a$")):
        try:
            return pwd_context.verify(plain_password, hashed_password)
        except Exception:
            pass
    # Fallback verification
    expected = hash_password(plain_password)
    return hmac.compare_digest(expected, hashed_password)


# ---------------------------------------------------------------------------
# JWT Configuration & Utilities
# ---------------------------------------------------------------------------

JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "stellar_ai_super_secret_jwt_key_2026")
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 Hours


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Generate a signed JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire, "iat": datetime.utcnow()})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> Optional[Dict[str, Any]]:
    """Decode and validate a JWT access token, returning the payload if valid."""
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        return payload
    except Exception:
        return None


# ---------------------------------------------------------------------------
# Internal Service Authentication & JWT Validation
# ---------------------------------------------------------------------------

INTERNAL_SERVICE_SECRET = os.getenv(
    "INTERNAL_SERVICE_SECRET", "stellar_secret_internal_microservice_key_2026"
)

try:
    from fastapi import Header, HTTPException, Depends
    FASTAPI_INJECT_AVAILABLE = True
except ImportError:
    FASTAPI_INJECT_AVAILABLE = False
    def Header(default=None, **kwargs): return default
    def Depends(fn=None): return None
    class HTTPException(Exception):
        def __init__(self, status_code: int, detail: str):
            super().__init__(detail)
            self.status_code = status_code
            self.detail = detail


def verify_internal_service_key(
    x_internal_key: Optional[str] = Header(None, alias="X-Internal-Service-Key")
) -> bool:
    """
    Validate internal microservice secret key for service-to-service calls
    between Express API Gateway and FastAPI microservice.
    Rejects unauthorized external requests with 403 Forbidden.
    """
    if not x_internal_key or not hmac.compare_digest(str(x_internal_key), INTERNAL_SERVICE_SECRET):
        raise HTTPException(
            status_code=403,
            detail="Forbidden: Invalid or missing X-Internal-Service-Key header."
        )
    return True


def verify_authenticated_caller(
    authorization: Optional[str] = Header(None, alias="Authorization"),
    x_internal_key: Optional[str] = Header(None, alias="X-Internal-Service-Key")
) -> Dict[str, Any]:
    """
    Dual-layer authentication verifier:
    Allows requests from either:
    1. Express API Gateway (via valid X-Internal-Service-Key header), OR
    2. Direct user client requests with valid Bearer JWT access token.
    Prevents unauthorized direct access to FastAPI internal endpoints.
    """
    # Allow bypassing authentication in explicit local test mode if configured
    if os.getenv("DISABLE_AUTH_FOR_TESTS", "").lower() in ("true", "1"):
        return {"auth_type": "test_bypass", "user": None, "is_internal": True}

    # 1. Service-to-service call from Express Gateway
    if x_internal_key and hmac.compare_digest(str(x_internal_key), INTERNAL_SERVICE_SECRET):
        user_payload = None
        if authorization and authorization.startswith("Bearer "):
            token = authorization.split(" ")[1]
            user_payload = decode_access_token(token)
        return {"auth_type": "internal_service", "user": user_payload, "is_internal": True}

    # 2. Direct user client call with JWT
    if authorization and authorization.startswith("Bearer "):
        token = authorization.split(" ")[1]
        payload = decode_access_token(token)
        if payload:
            return {"auth_type": "jwt_user", "user": payload, "is_internal": False}

    raise HTTPException(
        status_code=401,
        detail="Unauthorized: Valid Authorization Bearer token or X-Internal-Service-Key required."
    )


# ---------------------------------------------------------------------------
# Database & User Model Setup
# ---------------------------------------------------------------------------

Base = declarative_base()


class User(Base):
    """PostgreSQL User table model."""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "email": self.email,
            "username": self.username,
            "full_name": self.full_name,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


# Database Connection Initialization (PostgreSQL with SQLite Fallback)
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/stellar_db")

def init_db():
    """Attempt connecting to PostgreSQL, falling back to SQLite if offline."""
    global engine, SessionLocal
    try:
        engine = create_engine(DATABASE_URL, pool_pre_ping=True)
        Base.metadata.create_all(bind=engine)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        # Test connection
        with engine.connect() as conn:
            pass
        print(f"[AUTH DB] Successfully connected to PostgreSQL at {DATABASE_URL}")
    except Exception as e:
        print(f"[AUTH DB] PostgreSQL unavailable ({e}). Falling back to local SQLite database.")
        sqlite_url = "sqlite:///./stellar_auth.db"
        engine = create_engine(sqlite_url, connect_args={"check_same_thread": False})
        Base.metadata.create_all(bind=engine)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


init_db()


def get_db():
    """FastAPI Dependency for database sessions."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ---------------------------------------------------------------------------
# Pydantic Authentication Schemas
# ---------------------------------------------------------------------------

class UserCreate(BaseModel):
    email: str = Field(..., description="User email address")
    username: str = Field(..., description="Unique username")
    password: str = Field(..., min_length=6, description="User password (min 6 chars)")
    full_name: Optional[str] = Field(None, description="User full name")


class UserLogin(BaseModel):
    username_or_email: str = Field(..., description="Username or Email address")
    password: str = Field(..., description="Password")


class UserResponse(BaseModel):
    id: int
    email: str
    username: str
    full_name: Optional[str] = None
    is_active: bool = True
    created_at: Optional[str] = None


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
