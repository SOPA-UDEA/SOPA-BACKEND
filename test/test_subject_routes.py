import pytest
from httpx import AsyncClient, ASGITransport
from asgi_lifespan import LifespanManager
from src.main import app

@pytest.mark.asyncio
async def test_read_all_subjects():
    async with LifespanManager(app):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/subject/lists")
            assert response.status_code == 200

            data = response.json()
            assert isinstance(data, list)

@pytest.mark.asyncio
async def test_read_subjects_by_pensum():
    pensum_id = 29

    async with LifespanManager(app):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get(f"/subject/by_pensum/{pensum_id}")
            assert response.status_code == 200

            data = response.json()
            assert isinstance(data, list)