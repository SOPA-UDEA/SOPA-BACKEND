import pytest

@pytest.mark.asyncio
async def test_read_all_groups(client):
    response = await client.get("/group/lists")
    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, list)

    for item in data:
        assert isinstance(item, dict)
        assert isinstance(item["id"], int)
        assert isinstance(item["groupSize"], int)
        assert isinstance(item["modality"], str)
        assert isinstance(item["code"], int)
        assert isinstance(item["mirrorGroupId"], int)
        assert isinstance(item["subjectId"], int)
        assert isinstance(item["academicSchedulePensumId"], int)

# class GroupRequest(BaseModel):
#     groupSize: int = Field(gt=0)
#     modality: str = Field(min_length=4, max_length=150)
#     code: int = Field(gt=0)
#     mirrorGroupId: int = Field(gt=0)
#     subjectId: int = Field(gt=0)
#     academicSchedulePensumId: int = Field(gt=0)

@pytest.mark.asyncio
async def test_create_group(client):
    response = await client.post("/group/create", json={
        "group": {
            "groupSize": 2,
            "modality": "virtual",
            "code": 1,
            "mirrorGroupId": 4,
            "subjectId": 100,
            "academicSchedulePensumId": 1
        },
        "mirror": {
            "name": "Test Group"
        },
        "academic": {
            "pensumId": 30,
            "academicScheduleId": 1
        }
    })
    assert response.status_code == 201
    
    id = response.json().get("id")
    assert id is not None

    update_response = await client.put(f"/group/update/{id}", json={"groupSize": 3, "modality": "in-person", "code": 2, "mirrorGroupId": 5, "subjectId": 101, "academicSchedulePensumId": 5})
    assert update_response.status_code == 200

    delete_response = await client.delete(f"/group/delete/{id}")
    assert delete_response.status_code == 200
    assert delete_response.json().get("detail") == "Group deleted successfully"


