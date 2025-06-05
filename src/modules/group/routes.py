

from typing import List
from fastapi import APIRouter
from pydantic import BaseModel
from src.modules.academic_program.services import get_program_by_id
from src.modules.pensum.services import get_pensum_by_id
from src.modules.academic_schedule.routes import ScheduleRequest
from src.modules.schedule_x_group.services import create_schedule_pensum, get_schedule_pensum_by_pensum_id_and_schedule_id
from src.modules.group_classroom.services import delete_group_classroom
from src.modules.subject.services import get_subject_by_id, get_subjects_by_pensum_id
from src.modules.group.services import  add_group_base, create_classroom_x_group, exist_base_groups, get_all_groups_by_schedule_pensum_id, get_groups_by_subjectId_and_academicSchedulePenusmId, soft_delete_group, updata_group_schedule
from src.modules.group.services import add_group, update_group_by_id, delete_group_by_id, get_groups_by_academic_schedule_id, get_group_by_id
from src.modules.mirror_group.services import create_mirror_group, get_mirror_group_by_name
import random 
import string
from fastapi import HTTPException
from starlette import status
from src.modules.group.models import GroupCreationRequest, GroupRequest, GroupResponse, GroupUpdateRequest


router = APIRouter(
    tags=["group"],
)

class BaseGroup(BaseModel):
    schedule: int
    pensumIds: list[int]

@router.post("/schedule/{schedule_id}/list", response_model=List[GroupResponse])
async def get_groups_by_penseum(schedule_id: int, pensumIds: list[int]):
    try:
        schedule_pensums_id = []
        for pensumId in pensumIds:
            schedule_pensum = await get_schedule_pensum_by_pensum_id_and_schedule_id(pensumId, schedule_id)
            schedule_pensums_id.append(schedule_pensum.id)
        groups = await get_all_groups_by_schedule_pensum_id(schedule_pensums_id)
        return groups
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    

@router.post("/create/baseGroup/{schedule}")
async def create_baseGroups(schedule: int, pensumIds: list[int]):
    for pensumId in pensumIds:
        schedule_pensum = await get_schedule_pensum_by_pensum_id_and_schedule_id(pensumId, schedule)
        basegroups = await exist_base_groups(schedule_pensum.id)
        if basegroups is None:
            pensum = await get_pensum_by_id(pensumId)
            subjects = await get_subjects_by_pensum_id(pensumId)
            academicProgram = await get_program_by_id(pensum.academicProgramId)
            for subject in subjects:
                groupData = {
                    'group': {
                        'groupSize': 0,
                        'modality': academicProgram.modalityAcademic,
                        'code': 1 ,
                        'mirrorGroupId': 1,
                        'subjectId': subject.id, 
                        'academicSchedulePensumId': schedule_pensum.id,
                        'maxSize': 0,
                        'registeredPlaces': 0,
                    },
                    'mirror': {
                        'name': "Grupo espejo A",
                    },
                }
                iniciales = ''.join([p[0] for p in subject.name.split()])
                groupData['mirror']['name'] = iniciales + ''.join(random.choices(string.ascii_letters + string.digits, k=5))
                mirrorGroup = await create_mirror_group(groupData['mirror'])
                groupData['group']['mirrorGroupId'] = mirrorGroup.id
                await add_group_base(groupData['group'])
    return "Groups created succsessfuly"

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

        academic_schedule_pensum = await get_schedule_pensum_by_pensum_id_and_schedule_id(
            pensum_id, academic_schedule_id
        )
        if academic_schedule_pensum is None:
            academic_schedule_pensum = await create_schedule_pensum(academicSchedulePensumRequest.model_dump())
        group_request.mirrorGroupId = mirrorGroup.id
        group_request.academicSchedulePensumId = academic_schedule_pensum.id
        await add_group(group_request)
        return 'Group created successfully'
    except Exception as e:
        raise HTTPException(status_code=422, detail=str(e))

@router.put("/update/{groupId}", status_code=status.HTTP_204_NO_CONTENT)
async def update_group(groupId: int, group_request: GroupUpdateRequest):
    try:
     await update_group_by_id(groupId, group_request)
    except Exception as e:
        raise HTTPException(status_code=422, detail=str(e))
    
@router.delete("/delete/{groupId}", status_code=status.HTTP_200_OK)
async def delete_group(groupId: int):
    try:
        group = await get_group_by_id(groupId)
        groups = await get_groups_by_subjectId_and_academicSchedulePenusmId(group.subjectId, group.academicSchedulePensumId)
        if len(groups) > 1:
            await delete_group_classroom(groupId)
            await delete_group_by_id(groupId)
            return "Group deleted successfully"
        await soft_delete_group(groupId)
        return "Group soft deleted"
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Group with id {groupId} not found")

@router.get("/schedule/{academicScheduleId}/list", status_code=status.HTTP_200_OK, response_model=List[GroupResponse])
async def get_groups_by_academic_schedule(academicScheduleId: int):
    try:
        groups = await get_groups_by_academic_schedule_id(academicScheduleId)
        if not groups:
            raise HTTPException(status_code=404, detail="No groups found")
        return groups
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))
    
@router.put("/update/schedule/{group_x_classroom_id}", status_code=status.HTTP_202_ACCEPTED)
async def update_group_schedule(group_x_classroom_id: int, schedule: str):
    try:
        await updata_group_schedule(group_x_classroom_id, schedule)
        return 'schedule updated successfuly'
    except Exception as e: 
        raise HTTPException(status_code=422, detail=str(e))
    

@router.post("/create-of/{group_id}", status_code=status.HTTP_201_CREATED)
async def create_group_of(group_id: int):
    try:
        group = await get_group_by_id(group_id)
        subject = await get_subject_by_id(group.subjectId)
        iniciales = ''.join([p[0] for p in subject.name.split()])
        name = iniciales + ''.join(random.choices(string.ascii_letters + string.digits, k=5))
        mirror_group_data = {
            'name': name
        }
        mirror_group = await create_mirror_group(mirror_group_data)
        groupData = {
            'groupSize': group.groupSize,
            'modality': group.modality,
            'code':  group.code + 1,
            'mirrorGroupId': mirror_group.id,
            'subjectId': group.subjectId, 
            'academicSchedulePensumId': group.academicSchedulePensumId,
            'maxSize': group.maxSize,
            'registeredPlaces': group.registeredPlaces,
        }
        await add_group(GroupRequest(**groupData))
        print(1)
        return 'Group created'
    except Exception as e:
        raise HTTPException(status_code=422, detail=str(e))
        


 # groupData = {
        #     'group': {
        #         'groupSize': group.groupSize,
        #         'modality': group.modality,
        #         'code':  0,
        #         'mirrorGroupId': mirror_group.id,
        #         'subjectId': group.subjectId, 
        #         'academicSchedulePensumId': group.academicSchedulePensumId,
        #         'maxSize': group.maxSize,
        #         'registeredPlaces': group.registeredPlaces,
        #     },
        #     'mirror': {
        #         'name': "Grupo espejo A",
        #     },
        # }