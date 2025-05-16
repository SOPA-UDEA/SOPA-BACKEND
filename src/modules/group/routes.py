

from typing import List
from fastapi import APIRouter
from pydantic import BaseModel, Field
from src.modules.group.services import get_all_groups, add_group, update_group_by_id, delete_group_by_id, create_academic_schedule_pesnum, get_groups_by_academic_schedule_id, get_academic_schedule_pensum_by_pensum_id_and_academic_schedule_id
from src.modules.mirror_group.services import create_mirror_group
import random 
import string
from fastapi import HTTPException
from starlette import status

class GroupRequest(BaseModel):
    groupSize: int = Field(gt=0)
    modality: str = Field(min_length=4, max_length=150)
    code: int = Field(gt=0)
    mirrorGroupId: int
    subjectId: int = Field(gt=0)
    academicSchedulePensumId: int
class AcademicSchedulePensumRequest(BaseModel):
    pensumId: int = Field(gt=0)
    academicScheduleId: int = Field(gt=0)

class MirrorGroupRequest(BaseModel):
    name: str

class GroupCreationRequest(BaseModel):
    group: GroupRequest
    mirror: MirrorGroupRequest
    academic: AcademicSchedulePensumRequest

class GroupResponse(BaseModel):
    id: int
    groupSize: int
    modality: str 
    code: int 
    mirrorGroupId: int 
    subjectId: int 
    academicSchedulePensumId: int 

router = APIRouter(
    tags=["group"],
)

@router.get("/lists", status_code=status.HTTP_200_OK, response_model=List[GroupResponse])
async def create_group_list():
    groups = await get_all_groups()
    if not groups:
        raise HTTPException(status_code=404, detail="No groups found")
    return groups

@router.post("/create", status_code=status.HTTP_201_CREATED, response_model=GroupResponse)
async def create_group(request: GroupCreationRequest):
    group_request = request.group
    mirror_group_request = request.mirror
    academicSchedulePensumRequest = request.academic
    try:
        mirror_group_request.name = ''.join(random.choices(string.ascii_letters + string.digits, k=20))
        mirrorGroup = await create_mirror_group(mirror_group_request.model_dump())
        
        pensum_id = academicSchedulePensumRequest.pensumId
        academic_schedule_id = academicSchedulePensumRequest.academicScheduleId

        academic_schedule_pensum = await get_academic_schedule_pensum_by_pensum_id_and_academic_schedule_id(
            pensum_id, academic_schedule_id
        )

        if academic_schedule_pensum is None:
            academic_schedule_pensum_data = academicSchedulePensumRequest.model_dump()
            academic_schedule_pensum = await create_academic_schedule_pesnum(academic_schedule_pensum_data)

        group_request.mirrorGroupId = mirrorGroup.id
        group_request.academicSchedulePensumId = academic_schedule_pensum.id
        group_data = group_request.model_dump()
        group = await add_group(group_data)
        return group
    except Exception as e:
        raise HTTPException(status_code=422, detail=str(e))

@router.put("/update/{groupId}", status_code=status.HTTP_200_OK, response_model=GroupResponse)
async def update_group(groupId: int, group_request: GroupRequest):
    try:
        updated_group = await update_group_by_id(groupId, group_request.model_dump())
        return updated_group
    except Exception as e:
        raise HTTPException(status_code=422, detail=str(e))

    
    
@router.delete("/delete/{groupId}", status_code=status.HTTP_200_OK)
async def delete_group(groupId: int):
    try:
        await delete_group_by_id(groupId)
        return {"detail": "Group deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Group with id {groupId} not found")

@router.get("/academic_schedule/{academicScheduleId}/groups", status_code=status.HTTP_200_OK, response_model=List[GroupResponse])
async def get_groups_by_academic_schedule(academicScheduleId: int):
    try:
        print("hola 0")
        groups = await get_groups_by_academic_schedule_id(academicScheduleId)
        if not groups:
            raise HTTPException(status_code=404, detail="No groups found")
        return groups
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))
