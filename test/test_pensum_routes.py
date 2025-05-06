import pytest
from httpx import AsyncClient, ASGITransport
from asgi_lifespan import LifespanManager
from src.main import app

@pytest.mark.asyncio
async def test_get_pensum():
    async with LifespanManager(app):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/pensum/lists")
            assert response.status_code == 200


