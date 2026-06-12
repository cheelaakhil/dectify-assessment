"""
Authentication service – JWT generation, password hashing, token validation.
Stores *hashed* refresh tokens in the database for production-grade security.
"""
import os
import hashlib
import secrets
from datetime import datetime, timedelta, timezone

import bcrypt
from jose import jwt, JWTError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.models.token import RefreshToken

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
JWT_SECRET = os.getenv("JWT_SECRET", "change-me")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "15"))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))


# ---------------------------------------------------------------------------
# Password helpers (using bcrypt directly — passlib is incompatible with bcrypt>=5)
# ---------------------------------------------------------------------------
def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))


# ---------------------------------------------------------------------------
# Token helpers
# ---------------------------------------------------------------------------
def _hash_token(token: str) -> str:
    """SHA-256 hash of a refresh token for safe DB storage."""
    return hashlib.sha256(token.encode()).hexdigest()


def create_access_token(user_id: int, email: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {"sub": str(user_id), "email": email, "exp": expire, "type": "access"}
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def decode_access_token(token: str) -> dict | None:
    """Decode and validate an access token. Returns payload or None."""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        if payload.get("type") != "access":
            return None
        return payload
    except JWTError:
        return None


def generate_refresh_token() -> str:
    """Generate a cryptographically secure random refresh token."""
    return secrets.token_urlsafe(64)


# ---------------------------------------------------------------------------
# Database operations
# ---------------------------------------------------------------------------
async def get_user_by_email(db: AsyncSession, email: str) -> User | None:
    result = await db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()


async def create_user(db: AsyncSession, name: str, email: str, password: str) -> User:
    user = User(name=name, email=email, password_hash=hash_password(password))
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def store_refresh_token(db: AsyncSession, user_id: int, raw_token: str) -> None:
    """Store a *hashed* refresh token in the database."""
    token_record = RefreshToken(
        user_id=user_id,
        token_hash=_hash_token(raw_token),
        expires_at=datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS),
    )
    db.add(token_record)
    await db.commit()


async def validate_refresh_token(db: AsyncSession, raw_token: str) -> RefreshToken | None:
    """Find a valid (non-revoked, non-expired) refresh token by its hash."""
    token_hash = _hash_token(raw_token)
    result = await db.execute(
        select(RefreshToken).where(
            RefreshToken.token_hash == token_hash,
            RefreshToken.revoked == False,  # noqa: E712
            RefreshToken.expires_at > datetime.now(timezone.utc),
        )
    )
    return result.scalar_one_or_none()


async def revoke_refresh_token(db: AsyncSession, raw_token: str) -> bool:
    """Revoke a refresh token. Returns True if found and revoked."""
    token_hash = _hash_token(raw_token)
    result = await db.execute(
        select(RefreshToken).where(RefreshToken.token_hash == token_hash)
    )
    token_record = result.scalar_one_or_none()
    if token_record:
        token_record.revoked = True
        await db.commit()
        return True
    return False


async def revoke_all_user_tokens(db: AsyncSession, user_id: int) -> None:
    """Revoke all refresh tokens for a user (full logout)."""
    result = await db.execute(
        select(RefreshToken).where(
            RefreshToken.user_id == user_id,
            RefreshToken.revoked == False,  # noqa: E712
        )
    )
    tokens = result.scalars().all()
    for t in tokens:
        t.revoked = True
    await db.commit()
