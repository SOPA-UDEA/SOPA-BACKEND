import pytest

@pytest.mark.asyncio
async def test_get_academic_schedule(client):
    response = await client.get("/academic_schedule/lists")
    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, list)

    for item in data:
        assert isinstance(item, dict)
        assert isinstance(item["id"], int)
        assert isinstance(item["semester"], str)

@pytest.mark.asyncio
async def test_create_academic_schedule_by_id(client):
    response = await client.post("/academic_schedule/create", json={"semester": "2023-2"})
    assert response.status_code == 201

    data = response.json()
    assert isinstance(data, dict)
    assert isinstance(data["id"], int)
    assert isinstance(data["semester"], str)

    schedule_id = data["id"]
    delete_response = await client.delete(f"/academic_schedule/delete/{schedule_id}")
    assert delete_response.status_code == 204

@pytest.mark.asyncio
async def test_get_academic_schedule_by_id(client):
  
    create_response = await client.post("/academic_schedule/create", json={"semester": "2025-1"})
    assert create_response.status_code == 201
    created = create_response.json()
    schedule_id = created["id"]

   
    get_response = await client.get(f"/academic_schedule/academic_schedule/{schedule_id}")
    assert get_response.status_code == 200

    data = get_response.json()
    assert isinstance(data, dict)
    assert data["id"] == schedule_id
    assert data["semester"] == "2025-1"

    invalid_id = 999999
    error_response = await client.get(f"/academic_schedule/academic_schedule/{invalid_id}")
    assert error_response.status_code == 404
    assert error_response.json()["detail"] == "Academic schedule not found"

    await client.delete(f"/academic_schedule/delete/{schedule_id}")


