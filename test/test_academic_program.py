import pytest

@pytest.mark.asyncio
async def test_get_academic_program(client):
    response = await client.get("/academic_program/lists")
    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, list)

    for item in data:
        assert isinstance(item, dict)
        assert isinstance(item["id"], int)
        assert isinstance(item["name"], str)
        assert isinstance(item["code"], str)
        assert isinstance(item["modalityAcademic"], str)
        assert isinstance(item["headquarter"], str)
        assert isinstance(item["version"], int)
        assert isinstance(item["modalityId"], int)
        assert isinstance(item["facultyId"], int)
        assert isinstance(item["departmentId"], int)

