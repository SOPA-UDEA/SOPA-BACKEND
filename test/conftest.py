import pytest_asyncio
from src.database import database

@pytest_asyncio.fixture(scope="function")
async def db():
    await database.connect()
    yield
    await database.disconnect()