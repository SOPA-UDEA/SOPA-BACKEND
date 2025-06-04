import pytest

@pytest.mark.asyncio
async def test_get_pensum(client):
    response = await client.get("/pensum/lists")
    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, list)

    for item in data:
        assert isinstance(item, dict)
        assert isinstance(item["id"], int)
        assert isinstance(item["version"], int)
        assert isinstance(item["academicProgramId"], int)



