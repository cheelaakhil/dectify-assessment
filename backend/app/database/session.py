"""
Database session and engine configuration.
"""
import os
import logging
from urllib.parse import urlparse, quote_plus, urlunparse
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase

logger = logging.getLogger("spacetoday.database")

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./spacetoday.db")

# ---------------------------------------------------------------------------
# Normalise PostgreSQL URLs for SQLAlchemy + psycopg (async)
# ---------------------------------------------------------------------------
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+psycopg://", 1)
elif DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+psycopg://", 1)

# Validate the URL looks well-formed when PostgreSQL is in use
if "postgresql" in DATABASE_URL:
    try:
        parsed = urlparse(DATABASE_URL)
        if not parsed.hostname:
            logger.error("DATABASE_URL has no hostname – check for unescaped "
                         "special characters in the password (use URL-encoding).")
        elif "@" in (parsed.hostname or ""):
            logger.error("DATABASE_URL hostname contains '@' – the password likely "
                         "contains unescaped special characters. URL-encode them.")
        else:
            logger.info("DATABASE_URL host=%s port=%s db=%s",
                        parsed.hostname, parsed.port, parsed.path)
    except Exception as exc:
        logger.error("Failed to parse DATABASE_URL: %s", exc)

    if "?" not in DATABASE_URL:
        DATABASE_URL += "?sslmode=require"

engine = create_async_engine(DATABASE_URL, echo=False, pool_pre_ping=True)
AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


async def get_db() -> AsyncSession:
    """FastAPI dependency that yields a database session."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
