import pytest
import random
from httpx import AsyncClient, ASGITransport
from asgi_lifespan import LifespanManager
from src.main import app
from src.modules.classroom.models import ClassroomRequest

classroom_data = ClassroomRequest(
    capacity=30,
    location="Aula" + str(random.randint(1, 200)),
    ownDepartment=True,
    virtualMode=False
)

classroom_data2 = ClassroomRequest(
    capacity=30,
    location="Aula" + str(random.randint(1, 200)),
    ownDepartment=True,
    virtualMode=False
)

existing_classroom_data = ClassroomRequest(
    capacity=30,
    location="21308",
    ownDepartment=True,
    virtualMode=False
)

#create a test for the classroom creation endpoint
@pytest.mark.asyncio
async def test_create_classroom():
    async with LifespanManager(app):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post("/classroom/create", json=classroom_data.model_dump())
            assert response.status_code == 200
            data = response.json()
            assert data["location"] == classroom_data.location
            assert data["capacity"] == classroom_data.capacity
            assert data["ownDepartment"] == classroom_data.ownDepartment
            assert data["virtualMode"] == classroom_data.virtualMode
            assert "id" in data

#create a test for a classroom creation that already exists
@pytest.mark.asyncio
async def test_create_classroom_already_exists():
    async with LifespanManager(app):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post("/classroom/create", json=existing_classroom_data.model_dump())
            print("Status code:", response.status_code)
            print("Response:", response.text)
            assert response.status_code == 500
            data = response.json()
            assert data["detail"] == "Unique constraint failed on the fields: (`location`)"

#create a test for the classroom update endpoint
@pytest.mark.asyncio
async def test_update_classroom():
    async with LifespanManager(app):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.put(f"/classroom/update/375", json=classroom_data2.model_dump())
            assert response.status_code == 200
            data = response.json()
            assert data["location"] == classroom_data2.location
            assert data["capacity"] == classroom_data2.capacity
            assert data["ownDepartment"] == classroom_data2.ownDepartment
            assert data["virtualMode"] == classroom_data2.virtualMode

#Create a test to get the list of classrooms
@pytest.mark.asyncio
async def test_get_classroom_list():
    async with LifespanManager(app):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/classroom/list")
            assert response.status_code == 200
            data = response.json()
            assert isinstance(data, list)
            assert len(data) > 0

#Create a test to delete a classroom
@pytest.mark.asyncio
async def test_delete_classroom():
    async with LifespanManager(app):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.delete(f"/classroom/delete/375")
            assert response.status_code == 204