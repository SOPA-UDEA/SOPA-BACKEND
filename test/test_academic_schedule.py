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

