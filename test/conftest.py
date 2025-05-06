import pytest
from src.database import database

@pytest.fixture(scope="function", autouse=True)
async def db():
    await database.connect()
    yield
    await database.disconnect()