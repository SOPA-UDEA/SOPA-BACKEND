from typing import Optional
import pytest

@pytest.mark.asyncio
async def test_read_all_subjects(client):
    response = await client.get("/subject/lists")
    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, list)

    for item in data:
        assert isinstance(item, dict)
        assert isinstance(item["id"], int)
        assert isinstance(item["name"], str)
        assert isinstance(item["level"], int)
        assert isinstance(item["fields"], dict)
        assert isinstance(item["code"], str)
        assert isinstance(item["credits"], int)
        assert isinstance(item["weeklyHours"], int)
        assert isinstance(item["weeks"], int)
        assert isinstance(item["validable"], bool)
        assert isinstance(item["enableable"], bool)
        assert isinstance(item["coRequirements"], str)
        assert isinstance(item["creditRequirements"], Optional[str])
        assert isinstance(item["pensumId"], int)

@pytest.mark.asyncio
async def test_read_subjects_by_pensum(client):
    response = await client.get("/pensum/lists")
    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, list)

    pensum_id = data[0]["id"]

    response = await client.get(f"/subject/by_pensum/{pensum_id}")
    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, list)
    
    for item in data:
        assert isinstance(item, dict)
        assert isinstance(item["id"], int)
        assert isinstance(item["name"], str)
        assert isinstance(item["level"], int)
        assert isinstance(item["fields"], dict)
        assert isinstance(item["code"], str)
        assert isinstance(item["credits"], int)
        assert isinstance(item["weeklyHours"], int)
        assert isinstance(item["weeks"], int)
        assert isinstance(item["validable"], bool)
        assert isinstance(item["enableable"], bool)
        assert isinstance(item["coRequirements"], str)
        assert isinstance(item["creditRequirements"], Optional[str])
        assert isinstance(item["pensumId"], int)