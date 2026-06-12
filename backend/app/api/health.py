"""
Health check endpoint.
"""
from fastapi import APIRouter
from app.database.session import engine
from app.services.cache_service import get_cache

router = APIRouter()


@router.get("/health")
async def health_check():
    """
    Returns the health status of the API, database, and cache layer.
    """
    # Database check
    db_status = "connected"
    try:
        async with engine.connect() as conn:
            await conn.execute(
                __import__("sqlalchemy").text("SELECT 1")
            )
    except Exception:
        db_status = "disconnected"

    # Cache check
    cache = get_cache()
    cache_ok = await cache.health_check()

    overall = "healthy" if (db_status == "connected" and cache_ok) else "degraded"

    return {
        "status": overall,
        "database": db_status,
        "cache": "connected" if cache_ok else "disconnected",
    }
