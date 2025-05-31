

from typing import List
from fastapi import APIRouter
from src.modules.subject.services import get_subject_by_id
from src.modules.group.services import get_all_groups, add_group, update_group_by_id, delete_group_by_id, create_academic_schedule_pesnum, get_groups_by_academic_schedule_id, get_academic_schedule_pensum_by_pensum_id_and_academic_schedule_id, create_classroom_x_group
from src.modules.mirror_group.services import create_mirror_group, get_mirror_group_by_name
import random 
import string
from fastapi import HTTPException
from starlette import status
from src.modules.group.models import GroupRequest, GroupCreationRequest, GroupResponse


router = APIRouter(
    tags=["group"],
)

@router.get("/lists", status_code=status.HTTP_200_OK, response_model=List[GroupResponse])
async def create_group_list():
    groups = await get_all_groups()
    if not groups:
        raise HTTPException(status_code=404, detail="No groups found")
    return groups

@router.post("/create", status_code=status.HTTP_201_CREATED)
async def create_group(request: GroupCreationRequest):
    group_request = request.group
    mirror_group_request = request.mirror
    academicSchedulePensumRequest = request.academic
    try:

       
        
        existing_mirror_group = await get_mirror_group_by_name(mirror_group_request.name)

        if existing_mirror_group:
            mirrorGroup = existing_mirror_group
        else:
            subject = await get_subject_by_id(group_request.subjectId)
            iniciales = ''.join([p[0] for p in subject.name.split()])
            mirror_group_request.name = iniciales + ''.join(random.choices(string.ascii_letters + string.digits, k=5))
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
        group = await add_group(group_request)
        classroom_x_group = {
            "mainSchedule": "L10-12|M10-12",
            "mainClassroomId": 1,
            "groupId": group.id,
        }
        await create_classroom_x_group(classroom_x_group)
        return 'Group created successfully'
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
        groups = await get_groups_by_academic_schedule_id(academicScheduleId)
        if not groups:
            raise HTTPException(status_code=404, detail="No groups found")
        return groups
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))
