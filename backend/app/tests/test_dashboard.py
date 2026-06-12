"""
Tests for the /space/dashboard endpoint.

Covers the assessment-required parallel fetching with partial failure handling,
which is a major evaluation point.
"""
import pytest
from httpx import AsyncClient
from unittest.mock import patch, AsyncMock

MOCK_APOD = {"title": "Test Nebula", "date": "2025-01-01", "url": "https://example.com/nebula.jpg"}
MOCK_MARS = {"photos": [{"id": 1, "img_src": "https://example.com/mars.jpg"}]}
MOCK_ASTEROIDS = {"element_count": 2, "near_earth_objects": {"2025-01-01": []}}
MOCK_EONET = {"events": [{"title": "Wildfire"}]}


def _mock_all_nasa():
    return patch.multiple(
        "app.services.nasa_service",
        get_apod=AsyncMock(return_value=MOCK_APOD),
        get_mars_photos=AsyncMock(return_value=MOCK_MARS),
        get_asteroids=AsyncMock(return_value=MOCK_ASTEROIDS),
        get_eonet_events=AsyncMock(return_value=MOCK_EONET),
    )


@pytest.mark.asyncio
class TestDashboard:
    """Dashboard parallel fetching tests."""

    async def test_dashboard_requires_auth(self, client: AsyncClient):
        resp = await client.get("/api/space/dashboard")
        assert resp.status_code in (401, 403)

    async def test_dashboard_returns_all_feeds(self, auth_client: AsyncClient):
        with _mock_all_nasa():
            resp = await auth_client.get("/api/space/dashboard")
        assert resp.status_code == 200
        data = resp.json()
        assert data["apod"]["title"] == "Test Nebula"
        assert "photos" in data["mars_photos"]
        assert data["asteroids"]["element_count"] == 2
        assert len(data["earth_events"]["events"]) == 1

    async def test_partial_failure_apod(self, auth_client: AsyncClient):
        """If APOD fails, other feeds should still succeed."""
        with patch.multiple(
            "app.services.nasa_service",
            get_apod=AsyncMock(side_effect=Exception("NASA timeout")),
            get_mars_photos=AsyncMock(return_value=MOCK_MARS),
            get_asteroids=AsyncMock(return_value=MOCK_ASTEROIDS),
            get_eonet_events=AsyncMock(return_value=MOCK_EONET),
        ):
            resp = await auth_client.get("/api/space/dashboard")
        assert resp.status_code == 200
        data = resp.json()
        assert "error" in data["apod"]
        assert "photos" in data["mars_photos"]
        assert "element_count" in data["asteroids"]
        assert "events" in data["earth_events"]

    async def test_all_feeds_fail(self, auth_client: AsyncClient):
        """Even if ALL feeds fail, response is 200 with error dicts."""
        with patch.multiple(
            "app.services.nasa_service",
            get_apod=AsyncMock(side_effect=Exception("fail")),
            get_mars_photos=AsyncMock(side_effect=Exception("fail")),
            get_asteroids=AsyncMock(side_effect=Exception("fail")),
            get_eonet_events=AsyncMock(side_effect=Exception("fail")),
        ):
            resp = await auth_client.get("/api/space/dashboard")
        assert resp.status_code == 200
        data = resp.json()
        for key in ("apod", "mars_photos", "asteroids", "earth_events"):
            assert "error" in data[key], f"{key} should contain an error dict"

    async def test_partial_failure_multiple(self, auth_client: AsyncClient):
        """Two out of four feeds fail – the remaining two should still work."""
        with patch.multiple(
            "app.services.nasa_service",
            get_apod=AsyncMock(return_value=MOCK_APOD),
            get_mars_photos=AsyncMock(side_effect=Exception("Mars API down")),
            get_asteroids=AsyncMock(return_value=MOCK_ASTEROIDS),
            get_eonet_events=AsyncMock(side_effect=Exception("EONET down")),
        ):
            resp = await auth_client.get("/api/space/dashboard")
        assert resp.status_code == 200
        data = resp.json()
        assert data["apod"]["title"] == "Test Nebula"
        assert "error" in data["mars_photos"]
        assert data["asteroids"]["element_count"] == 2
        assert "error" in data["earth_events"]
