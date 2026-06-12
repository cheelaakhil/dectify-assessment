"""
Tests for the authentication flow.
"""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
class TestAuth:
    """Full auth lifecycle: signup → login → refresh → me → logout."""

    async def test_signup_success(self, client: AsyncClient):
        resp = await client.post("/api/auth/signup", json={
            "name": "Test User",
            "email": "test@example.com",
            "password": "strongpass123",
        })
        assert resp.status_code == 201
        data = resp.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        # Refresh token should be in an HttpOnly cookie
        assert "refresh_token" in resp.cookies

    async def test_signup_duplicate_email(self, client: AsyncClient):
        # First signup
        await client.post("/api/auth/signup", json={
            "name": "User A",
            "email": "dup@example.com",
            "password": "pass123",
        })
        # Duplicate
        resp = await client.post("/api/auth/signup", json={
            "name": "User B",
            "email": "dup@example.com",
            "password": "pass456",
        })
        assert resp.status_code == 409

    async def test_login_success(self, client: AsyncClient):
        # Signup first
        await client.post("/api/auth/signup", json={
            "name": "Login User",
            "email": "login@example.com",
            "password": "mypassword",
        })
        # Login
        resp = await client.post("/api/auth/login", json={
            "email": "login@example.com",
            "password": "mypassword",
        })
        assert resp.status_code == 200
        assert "access_token" in resp.json()

    async def test_login_wrong_password(self, client: AsyncClient):
        await client.post("/api/auth/signup", json={
            "name": "Wrong Pass",
            "email": "wrong@example.com",
            "password": "correct",
        })
        resp = await client.post("/api/auth/login", json={
            "email": "wrong@example.com",
            "password": "incorrect",
        })
        assert resp.status_code == 401

    async def test_me_endpoint(self, client: AsyncClient):
        # Signup and get token
        signup = await client.post("/api/auth/signup", json={
            "name": "Me User",
            "email": "me@example.com",
            "password": "pass",
        })
        token = signup.json()["access_token"]

        resp = await client.get(
            "/api/auth/me",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["email"] == "me@example.com"
        assert data["name"] == "Me User"

    async def test_me_without_token(self, client: AsyncClient):
        resp = await client.get("/api/auth/me")
        assert resp.status_code == 403

    async def test_refresh_token_flow(self, client: AsyncClient):
        # Signup
        signup = await client.post("/api/auth/signup", json={
            "name": "Refresh User",
            "email": "refresh@example.com",
            "password": "pass",
        })
        refresh_cookie = signup.cookies.get("refresh_token")
        assert refresh_cookie is not None

        # Refresh
        resp = await client.post(
            "/api/auth/refresh",
            cookies={"refresh_token": refresh_cookie},
        )
        assert resp.status_code == 200
        assert "access_token" in resp.json()

    async def test_logout(self, client: AsyncClient):
        signup = await client.post("/api/auth/signup", json={
            "name": "Logout User",
            "email": "logout@example.com",
            "password": "pass",
        })
        refresh_cookie = signup.cookies.get("refresh_token")

        resp = await client.post(
            "/api/auth/logout",
            cookies={"refresh_token": refresh_cookie},
        )
        assert resp.status_code == 200
        assert resp.json()["message"] == "Logged out successfully"

        # Refresh should now fail
        resp2 = await client.post(
            "/api/auth/refresh",
            cookies={"refresh_token": refresh_cookie},
        )
        assert resp2.status_code == 401
