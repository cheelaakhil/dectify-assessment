"""
Shared pytest fixtures for the test suite.

Creates an isolated in-memory SQLite database and an httpx AsyncClient
for every test, so tests are fully independent.
"""
import os
import asyncio
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

# Force test env before importing the app
os.environ["DATABASE_URL"] = "sqlite+aiosqlite://"
os.environ["JWT_SECRET"] = "test-secret"
os.environ["NASA_API_KEY"] = "DEMO_KEY"

from app.database.session import Base, get_db
from main import app
from app.api.limiter import limiter

# Disable rate limiting for tests
limiter.enabled = False


# ---------------------------------------------------------------------------
# Event loop scope (pytest-asyncio)
# ---------------------------------------------------------------------------
@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


# ---------------------------------------------------------------------------
# Database fixtures
# ---------------------------------------------------------------------------
@pytest_asyncio.fixture
async def db_engine():
    engine = create_async_engine("sqlite+aiosqlite://", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture
async def db_session(db_engine):
    session_factory = async_sessionmaker(db_engine, class_=AsyncSession, expire_on_commit=False)
    async with session_factory() as session:
        yield session


# ---------------------------------------------------------------------------
# HTTP client fixture – overrides the DB dependency
# ---------------------------------------------------------------------------
@pytest_asyncio.fixture
async def client(db_engine):
    session_factory = async_sessionmaker(db_engine, class_=AsyncSession, expire_on_commit=False)

    async def _override_get_db():
        async with session_factory() as session:
            yield session

    app.dependency_overrides[get_db] = _override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()

@pytest_asyncio.fixture
async def auth_client(client: AsyncClient):
    signup_resp = await client.post("/api/auth/signup", json={
        "name": "Auth User",
        "email": "authclient@example.com",
        "password": "pass",
    })
    token = signup_resp.json()["access_token"]
    client.headers["Authorization"] = f"Bearer {token}"
    return client
