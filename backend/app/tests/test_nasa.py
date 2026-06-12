import pytest
from httpx import AsyncClient
from unittest.mock import patch

@pytest.fixture(autouse=True)
def mock_nasa_service():
    with patch("app.services.nasa_service.get_apod") as mock_apod, \
         patch("app.services.nasa_service.get_mars_photos") as mock_mars, \
         patch("app.services.nasa_service.get_asteroids") as mock_asteroids, \
         patch("app.services.nasa_service.get_eonet_events") as mock_eonet:
        
        mock_apod.return_value = {"title": "Mock APOD", "url": "http://mock.url/apod.jpg"}
        mock_mars.return_value = {"photos": [{"id": 1, "img_src": "http://mock.url/mars.jpg"}]}
        mock_asteroids.return_value = {"near_earth_objects": {}}
        mock_eonet.return_value = {"events": [{"title": "Mock Event"}]}
        
        yield

@pytest.mark.asyncio
async def test_get_apod(auth_client: AsyncClient):
    resp = await auth_client.get("/api/space/apod")
    assert resp.status_code == 200
    assert resp.json() == {"title": "Mock APOD", "url": "http://mock.url/apod.jpg"}

@pytest.mark.asyncio
async def test_get_mars_photos(auth_client: AsyncClient):
    resp = await auth_client.get("/api/space/mars-photos")
    assert resp.status_code == 200
    assert resp.json() == {"photos": [{"id": 1, "img_src": "http://mock.url/mars.jpg"}]}

@pytest.mark.asyncio
async def test_get_asteroids(auth_client: AsyncClient):
    resp = await auth_client.get("/api/space/asteroids")
    assert resp.status_code == 200
    assert resp.json() == {"near_earth_objects": {}}

@pytest.mark.asyncio
async def test_get_eonet(auth_client: AsyncClient):
    resp = await auth_client.get("/api/space/earth-events")
    assert resp.status_code == 200
    assert resp.json() == {"events": [{"title": "Mock Event"}]}
