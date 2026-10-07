"""
SkillSetu X — Security Module
JWT tokens with refresh rotation, OTP, password hashing.
"""
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any

import pyotp
from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import get_settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def create_access_token(data: dict[str, Any], expires_delta: timedelta | None = None) -> str:
    settings = get_settings()
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.jwt_access_token_expire_minutes)
    )
    to_encode.update({"exp": expire, "type": "access", "jti": str(uuid.uuid4())})
    return jwt.encode(to_encode, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def create_refresh_token(data: dict[str, Any]) -> str:
    settings = get_settings()
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=settings.jwt_refresh_token_expire_days)
    to_encode.update({
        "exp": expire, "type": "refresh",
        "jti": str(uuid.uuid4()),
        "family": data.get("family", str(uuid.uuid4())),
    })
    return jwt.encode(to_encode, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def decode_token(token: str) -> dict[str, Any]:
    settings = get_settings()
    try:
        return jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
    except JWTError as e:
        raise ValueError(f"Invalid token: {e}")


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def generate_otp(email: str) -> tuple[str, str]:
    settings = get_settings()
    secret = pyotp.random_base32()
    totp = pyotp.TOTP(secret, interval=settings.otp_expiry_seconds, digits=6)
    return totp.now(), secret


def verify_otp(otp: str, secret: str) -> bool:
    settings = get_settings()
    totp = pyotp.TOTP(secret, interval=settings.otp_expiry_seconds, digits=6)
    return totp.verify(otp, valid_window=1)


def create_token_pair(user_id: str, tenant_id: str, role: str) -> dict[str, str]:
    data = {"sub": user_id, "tenant_id": tenant_id, "role": role}
    family = str(uuid.uuid4())
    return {
        "access_token": create_access_token(data),
        "refresh_token": create_refresh_token({**data, "family": family}),
        "token_type": "bearer",
    }


def rotate_refresh_token(old_token: str) -> dict[str, str]:
    payload = decode_token(old_token)
    if payload.get("type") != "refresh":
        raise ValueError("Not a refresh token")
    data = {"sub": payload["sub"], "tenant_id": payload.get("tenant_id", ""), "role": payload.get("role", "")}
    return {
        "access_token": create_access_token(data),
        "refresh_token": create_refresh_token({**data, "family": payload.get("family", str(uuid.uuid4()))}),
        "token_type": "bearer",
    }
