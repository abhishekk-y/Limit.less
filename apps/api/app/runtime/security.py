import base64
import hashlib
import hmac
import secrets
from datetime import timedelta

from cryptography.fernet import Fernet
from fastapi import HTTPException
from jose import JWTError, jwt

from .models import RefreshSession, new_id, now


def is_superadmin(user) -> bool:
    """Check the database role assigned only by the private provisioning command."""
    return bool(user and user.role == "superadmin")


def hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    digest = hashlib.scrypt(password.encode(), salt=salt.encode(), n=16384, r=8, p=1).hex()
    return f"scrypt${salt}${digest}"


def verify_password(password: str, stored: str) -> bool:
    try:
        _, salt, expected = stored.split("$")
        actual = hashlib.scrypt(password.encode(), salt=salt.encode(), n=16384, r=8, p=1).hex()
        return hmac.compare_digest(actual, expected)
    except (ValueError, TypeError):
        return False


def decode(token, settings, kind="access"):
    try:
        payload = jwt.decode(
            token, settings.jwt_secret_key, algorithms=["HS256"], audience="skillsetu", issuer="skillsetu-api"
        )
        if payload.get("type") != kind or not all(payload.get(k) for k in ("sub", "jti", "exp")):
            raise ValueError("Invalid token claims")
        return payload
    except (JWTError, ValueError):
        raise HTTPException(401, "Session expired. Please sign in again.") from None


async def issue_tokens(db, user, settings, family=None):
    family = family or new_id()
    tokens = {}
    for kind, lifetime in (
        ("access", timedelta(minutes=settings.access_minutes)),
        ("refresh", timedelta(days=settings.refresh_days)),
    ):
        token_id = new_id()
        expiry = now() + lifetime
        payload = {
            "sub": user.id,
            "tenant_id": user.tenant_id,
            "type": kind,
            "jti": token_id,
            "family": family,
            "exp": expiry,
            "iat": now(),
            "aud": "skillsetu",
            "iss": "skillsetu-api",
        }
        tokens[f"{kind}_token"] = jwt.encode(payload, settings.jwt_secret_key, algorithm="HS256")
        if kind == "refresh":
            db.add(RefreshSession(id=token_id, user_id=user.id, family=family, expires_at=expiry))
    return {**tokens, "token_type": "bearer"}


def cipher(settings):
    return Fernet(base64.urlsafe_b64encode(hashlib.sha256(settings.vault_key.encode()).digest()))
