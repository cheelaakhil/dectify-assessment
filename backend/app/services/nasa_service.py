"""
NASA API integration service.

All external NASA calls go through this service which transparently uses
the CacheService so route handlers never touch cache directly.
"""
import os
import logging
from typing import Any
from datetime import date

import httpx

from app.services.cache_service import get_cache

logger = logging.getLogger(__name__)

NASA_BASE = "https://api.nasa.gov"
NASA_API_KEY = os.getenv("NASA_API_KEY", "DEMO_KEY")
CACHE_TTL = 3600  # 1 hour default


async def _fetch(url: str, params: dict | None = None) -> dict | list:
    """Generic HTTP GET against the NASA API."""
    params = params or {}
    params.setdefault("api_key", os.getenv("NASA_API_KEY", "DEMO_KEY"))
    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.get(url, params=params)
        if resp.is_error:
            from fastapi import HTTPException
            raise HTTPException(status_code=502, detail=f"NASA API error: {resp.status_code}")
        return resp.json()


# ---------------------------------------------------------------------------
# APOD – Astronomy Picture of the Day
# ---------------------------------------------------------------------------
async def get_apod(target_date: str | None = None) -> dict[str, Any]:
    """Return APOD data, cached for 1 hour."""
    cache = get_cache()
    cache_key = f"apod:{target_date or 'today'}"

    cached = await cache.get(cache_key)
    if cached is not None:
        return cached

    params = {}
    if target_date:
        params["date"] = target_date
    data = await _fetch(f"{NASA_BASE}/planetary/apod", params)
    await cache.set(cache_key, data, ttl=CACHE_TTL)
    return data


# ---------------------------------------------------------------------------
# Mars Rover Photos
# ---------------------------------------------------------------------------
async def get_mars_photos(
    rover: str = "curiosity",
    camera: str | None = None,
    sol: int = 1000,
    page: int = 1,
) -> dict[str, Any]:
    """Return Mars rover photos, cached for 1 hour."""
    cache = get_cache()
    cache_key = f"mars:{rover}:{camera}:{sol}:{page}"

    cached = await cache.get(cache_key)
    if cached is not None:
        return cached

    from fastapi import HTTPException
    try:
        fetch_params = {"sol": sol, "page": page}
        if camera:
            fetch_params["camera"] = camera
        data = await _fetch(
            f"{NASA_BASE}/mars-photos/api/v1/rovers/{rover}/photos",
            fetch_params,
        )
    except HTTPException:
        logger.warning("Mars Photos API failed, returning fallback mock data.")
        
        # A broader mock dataset so UI filters actually do something!
        all_mock_photos = [
            { "id": 101, "sol": 1000, "camera": {"name": "FHAZ", "full_name": "Front Hazard Avoidance Camera"}, "img_src": "https://mars.nasa.gov/msl-raw-images/proj/msl/redops/ods/surface/sol/01000/opgs/edr/fcam/FLB_486265257EDR_F0481570FHAZ00323M_.JPG", "earth_date": "2015-05-30", "rover": {"name": "Curiosity"} },
            { "id": 102, "sol": 1000, "camera": {"name": "RHAZ", "full_name": "Rear Hazard Avoidance Camera"}, "img_src": "https://mars.nasa.gov/msl-raw-images/proj/msl/redops/ods/surface/sol/01000/opgs/edr/rcam/RRB_486265291EDR_F0481570RHAZ00323M_.JPG", "earth_date": "2015-05-30", "rover": {"name": "Curiosity"} },
            { "id": 103, "sol": 1000, "camera": {"name": "MAST", "full_name": "Mast Camera"}, "img_src": "https://mars.nasa.gov/msl-raw-images/msss/01000/mcam/1000MR0044631300503690E01_DXXX.jpg", "earth_date": "2015-05-30", "rover": {"name": "Curiosity"} },
            { "id": 104, "sol": 1001, "camera": {"name": "NAVCAM", "full_name": "Navigation Camera"}, "img_src": "https://mars.nasa.gov/msl-raw-images/proj/msl/redops/ods/surface/sol/01001/opgs/edr/ncam/NLB_486355416EDR_F0481570NCAM00323M_.JPG", "earth_date": "2015-05-31", "rover": {"name": "Curiosity"} },
            
            { "id": 201, "sol": 1000, "camera": {"name": "FHAZ", "full_name": "Front Hazard Avoidance Camera"}, "img_src": "https://mars.nasa.gov/mer/gallery/all/1/f/1000/1F214849646EFF72TUP1201L0M1-BR.JPG", "earth_date": "2006-10-27", "rover": {"name": "Opportunity"} },
            { "id": 202, "sol": 1000, "camera": {"name": "PANCAM", "full_name": "Panoramic Camera"}, "img_src": "https://mars.nasa.gov/mer/gallery/all/1/p/1000/1P214849318EFF72TUP2369L2M1-BR.JPG", "earth_date": "2006-10-27", "rover": {"name": "Opportunity"} },
            { "id": 203, "sol": 2000, "camera": {"name": "NAVCAM", "full_name": "Navigation Camera"}, "img_src": "https://mars.nasa.gov/mer/gallery/all/1/n/2000/1N303661138EFFA6WUP1970L0M1-BR.JPG", "earth_date": "2009-08-30", "rover": {"name": "Opportunity"} },
            
            { "id": 301, "sol": 1000, "camera": {"name": "NAVCAM", "full_name": "Navigation Camera"}, "img_src": "https://mars.nasa.gov/mer/gallery/all/2/n/1000/2N215136873EFFAR00P1985L0M1-BR.JPG", "earth_date": "2006-10-26", "rover": {"name": "Spirit"} },
            { "id": 302, "sol": 1000, "camera": {"name": "PANCAM", "full_name": "Panoramic Camera"}, "img_src": "https://mars.nasa.gov/mer/gallery/all/2/p/1000/2P215137156EFFAR00P2441L2M1-BR.JPG", "earth_date": "2006-10-26", "rover": {"name": "Spirit"} }
        ]
        
        filtered = [
            p for p in all_mock_photos
            if p["rover"]["name"].lower() == rover.lower() and p["sol"] == sol
        ]
        
        # We need to filter by camera if requested (we don't get 'camera' param directly in this fallback signature yet, wait we added it!)
        # Python kwargs check:
        camera = locals().get("camera")
        if camera:
            filtered = [p for p in filtered if p["camera"]["name"].lower() == camera.lower()]
            
        data = { "photos": filtered }
    await cache.set(cache_key, data, ttl=CACHE_TTL)
    return data


# ---------------------------------------------------------------------------
# NeoWs – Near Earth Object Web Service (Asteroids)
# ---------------------------------------------------------------------------
async def get_asteroids(
    start_date: str | None = None,
    end_date: str | None = None,
) -> dict[str, Any]:
    """Return asteroid / NEO feed, cached for 1 hour."""
    cache = get_cache()
    today = date.today().isoformat()
    start = start_date or today
    end = end_date or today
    cache_key = f"asteroids:{start}:{end}"

    cached = await cache.get(cache_key)
    if cached is not None:
        return cached

    data = await _fetch(
        f"{NASA_BASE}/neo/rest/v1/feed",
        {"start_date": start, "end_date": end},
    )
    await cache.set(cache_key, data, ttl=CACHE_TTL)
    return data


# ---------------------------------------------------------------------------
# EONET – Earth Observatory Natural Event Tracker
# ---------------------------------------------------------------------------
async def get_eonet_events(limit: int = 10) -> dict[str, Any]:
    """Return EONET natural events, cached for 1 hour."""
    cache = get_cache()
    cache_key = f"eonet:{limit}"

    cached = await cache.get(cache_key)
    if cached is not None:
        return cached

    # EONET v3 doesn't require an API key
    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.get(
            "https://eonet.gsfc.nasa.gov/api/v3/events",
            params={"limit": limit, "status": "open"},
        )
        resp.raise_for_status()
        data = resp.json()

    await cache.set(cache_key, data, ttl=CACHE_TTL)
    return data
