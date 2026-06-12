"""
Unit tests for authentication service functions (no HTTP layer).

Covers the assessment-required areas:
  - Password hashing & verification
  - JWT access token generation & validation
  - Refresh token generation
  - Token hash security
"""
import pytest
from datetime import datetime, timedelta, timezone

from app.services.auth_service import (
    hash_password,
    verify_password,
    create_access_token,
    decode_access_token,
    generate_refresh_token,
    _hash_token,
    JWT_SECRET,
    JWT_ALGORITHM,
)


# ═══════════════════════════════════════════════════════════════════════════
# Password Hashing
# ═══════════════════════════════════════════════════════════════════════════
@pytest.mark.asyncio
class TestPasswordHashing:
    """Password hashing and verification using bcrypt."""

    async def test_hash_returns_string(self):
        hashed = hash_password("MyP@ssw0rd!")
        assert isinstance(hashed, str)
        assert len(hashed) > 0

    async def test_hash_is_not_plaintext(self):
        plain = "MyP@ssw0rd!"
        assert hash_password(plain) != plain

    async def test_different_calls_produce_different_hashes(self):
        """bcrypt uses a random salt each time."""
        h1 = hash_password("same")
        h2 = hash_password("same")
        assert h1 != h2

    async def test_verify_correct_password(self):
        plain = "CorrectHorseBatteryStaple"
        hashed = hash_password(plain)
        assert verify_password(plain, hashed) is True

    async def test_verify_wrong_password(self):
        hashed = hash_password("right")
        assert verify_password("wrong", hashed) is False

    async def test_verify_empty_password(self):
        hashed = hash_password("")
        assert verify_password("", hashed) is True
        assert verify_password("notempty", hashed) is False


# ═══════════════════════════════════════════════════════════════════════════
# JWT Access Tokens
# ═══════════════════════════════════════════════════════════════════════════
@pytest.mark.asyncio
class TestJWT:
    """JWT generation, decoding, and edge-case validation."""

    async def test_create_returns_string(self):
        token = create_access_token(user_id=1, email="a@b.com")
        assert isinstance(token, str) and len(token) > 0

    async def test_decode_valid_token(self):
        token = create_access_token(user_id=42, email="user@example.com")
        payload = decode_access_token(token)
        assert payload is not None
        assert payload["sub"] == "42"
        assert payload["email"] == "user@example.com"
        assert payload["type"] == "access"

    async def test_decode_invalid_token(self):
        assert decode_access_token("not.a.real.token") is None

    async def test_decode_tampered_token(self):
        token = create_access_token(user_id=1, email="a@b.com")
        # Change a character in the middle of the signature (the third part of the JWT)
        parts = token.split(".")
        if len(parts) == 3:
            sig = parts[2]
            tampered_sig = sig[:-5] + ("A" if sig[-5] != "A" else "B") + sig[-4:]
            tampered = f"{parts[0]}.{parts[1]}.{tampered_sig}"
        else:
            tampered = token[:-1] + "A"
        assert decode_access_token(tampered) is None

    async def test_decode_expired_token(self):
        """Manually craft an already-expired token."""
        from jose import jwt as jose_jwt
        payload = {
            "sub": "1", "email": "a@b.com",
            "exp": datetime.now(timezone.utc) - timedelta(seconds=10),
            "type": "access",
        }
        token = jose_jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
        assert decode_access_token(token) is None

    async def test_decode_wrong_type_rejected(self):
        """A token with type != 'access' should be rejected."""
        from jose import jwt as jose_jwt
        payload = {
            "sub": "1", "email": "a@b.com",
            "exp": datetime.now(timezone.utc) + timedelta(hours=1),
            "type": "refresh",
        }
        token = jose_jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
        assert decode_access_token(token) is None


# ═══════════════════════════════════════════════════════════════════════════
# Refresh Token Generation
# ═══════════════════════════════════════════════════════════════════════════
@pytest.mark.asyncio
class TestRefreshTokenGeneration:
    async def test_token_length(self):
        token = generate_refresh_token()
        assert len(token) > 50

    async def test_uniqueness(self):
        tokens = {generate_refresh_token() for _ in range(100)}
        assert len(tokens) == 100

    async def test_token_stored_as_hash(self):
        """The raw token should not equal its hash (SHA-256)."""
        raw = generate_refresh_token()
        hashed = _hash_token(raw)
        assert hashed != raw
        assert len(hashed) == 64  # SHA-256 hex digest
