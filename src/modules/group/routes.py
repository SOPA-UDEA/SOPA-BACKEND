

from typing import List
from fastapi import APIRouter
from pydantic import BaseModel, Field
from src.modules.group.services import get_all_groups, add_group, update_group_by_id, delete_group_by_id, create_academic_schedule_pesnum, get_academic_schedule_pensum_by_pensum_id_and_academic_schedule_id
from src.modules.mirror_group.services import create_mirror_group
import random 
import string
from fastapi import HTTPException


class GroupRequest(BaseModel):
    groupSize: int = Field(gt=0)
    modality: str = Field(min_length=4, max_length=150)
    code: int = Field(gt=0)
    mirrorGroupId: int = Field(gt=0)
    subjectId: int = Field(gt=0)
    academicSchedulePensumId: int = Field(gt=0)

class AcademicSchedulePensumRequest(BaseModel):
    pensumId: int = Field(gt=0)
    academicScheduleId: int = Field(gt=0)

class MirrorGroupRequest(BaseModel):
    name: str = Field(min_length=4, max_length=150)

router = APIRouter(
    tags=["group"],
)

@router.get("/lists")
async def create_group_list():
    groups = await get_all_groups()
    return {"groups": groups }

@router.post("/create")
async def create_group(group_request: GroupRequest, mirror_group_request: MirrorGroupRequest, academicSchedulePensumRequest: AcademicSchedulePensumRequest):
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
    return {
        "group": group,
        "mirrorGroup": mirrorGroup,
        "academicSchedulePensum": academic_schedule_pensum
    } 

@router.put("/update/{groupId}")
async def update_group(groupId: int, group_request: GroupRequest):
    try:
        updated_group = await update_group_by_id(groupId, group_request.model_dump())
        return updated_group
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Group with id {groupId} not found")

    
    
@router.delete("/delete/{groupId}")
async def delete_group(groupId: int):
    try:
        deleted_group = await delete_group_by_id(groupId)
        return deleted_group
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Group with id {groupId} not found")