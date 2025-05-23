import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from src.main import app
from src.database import database

@pytest_asyncio.fixture
async def client():
    await database.connect()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client
    await database.disconnect()