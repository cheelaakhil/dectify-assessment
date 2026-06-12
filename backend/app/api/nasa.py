"""
NASA data endpoints with parallel dashboard aggregation.
Uses asyncio.gather with return_exceptions=True for partial failure handling.
"""
import asyncio
import logging
from typing import Any

from fastapi import APIRouter, Depends, Query

from app.api.deps import get_current_user
from app.models.user import User
from app.services import nasa_service

router = APIRouter()
logger = logging.getLogger(__name__)


def _wrap_error(exc: Exception) -> dict[str, str]:
    """Convert an exception into a user-friendly error dict."""
    return {"error": f"Service unavailable: {type(exc).__name__}"}


# ---------------------------------------------------------------------------
# GET /dashboard – parallel aggregation of all NASA feeds
# ---------------------------------------------------------------------------
@router.get("/dashboard")
async def dashboard(current_user: User = Depends(get_current_user)) -> dict[str, Any]:
    """
    Aggregate APOD, Mars photos, asteroids, and EONET events in parallel.
    Individual failures are returned as error objects instead of crashing the
    entire response (partial failure handling).
    """
    results = await asyncio.gather(
        nasa_service.get_apod(),
        nasa_service.get_mars_photos(),
        nasa_service.get_asteroids(),
        nasa_service.get_eonet_events(),
        return_exceptions=True,
    )

    keys = ["apod", "mars_photos", "asteroids", "earth_events"]
    payload: dict[str, Any] = {}
    for key, result in zip(keys, results):
        if isinstance(result, Exception):
            logger.warning("Dashboard: %s failed – %s", key, result)
            payload[key] = _wrap_error(result)
        else:
            payload[key] = result

    return payload


# ---------------------------------------------------------------------------
# Individual endpoints
# ---------------------------------------------------------------------------
@router.get("/apod")
async def apod(
    date: str | None = Query(None, description="YYYY-MM-DD"),
    current_user: User = Depends(get_current_user),
):
    return await nasa_service.get_apod(target_date=date)


@router.get("/mars-photos")
async def mars_photos(
    rover: str = Query("curiosity"),
    camera: str | None = Query(None),
    sol: int = Query(1000),
    page: int = Query(1),
    current_user: User = Depends(get_current_user),
):
    return await nasa_service.get_mars_photos(rover=rover, camera=camera, sol=sol, page=page)


@router.get("/asteroids")
async def asteroids(
    start_date: str | None = Query(None),
    end_date: str | None = Query(None),
    current_user: User = Depends(get_current_user),
):
    return await nasa_service.get_asteroids(start_date=start_date, end_date=end_date)


@router.get("/earth-events")
async def earth_events(
    limit: int = Query(10),
    current_user: User = Depends(get_current_user),
):
    return await nasa_service.get_eonet_events(limit=limit)
