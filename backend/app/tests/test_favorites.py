import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_create_and_list_favorites(auth_client: AsyncClient):
    # Create
    create_resp = await auth_client.post("/api/favorites/", json={
        "item_type": "apod",
        "item_payload": {"title": "Test APOD"}
    })
    assert create_resp.status_code == 201
    fav = create_resp.json()
    assert fav["item_type"] == "apod"
    assert fav["item_payload"] == {"title": "Test APOD"}
    fav_id = fav["id"]

    # List
    list_resp = await auth_client.get("/api/favorites/")
    assert list_resp.status_code == 200
    favs = list_resp.json()
    assert len(favs) >= 1
    assert any(f["id"] == fav_id for f in favs)

@pytest.mark.asyncio
async def test_delete_favorite(auth_client: AsyncClient):
    create_resp = await auth_client.post("/api/favorites/", json={
        "item_type": "mars",
        "item_payload": {"rover": "curiosity"}
    })
    fav_id = create_resp.json()["id"]

    del_resp = await auth_client.delete(f"/api/favorites/{fav_id}")
    assert del_resp.status_code == 200

    list_resp = await auth_client.get("/api/favorites/")
    assert not any(f["id"] == fav_id for f in list_resp.json())

@pytest.mark.asyncio
async def test_delete_not_found(auth_client: AsyncClient):
    del_resp = await auth_client.delete("/api/favorites/9999")
    assert del_resp.status_code == 404
