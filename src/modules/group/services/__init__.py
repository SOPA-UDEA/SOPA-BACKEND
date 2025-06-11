from typing import List
from src.modules.group.models import GroupResponse
from src.modules.group_proffesor.services import update_group_proffesor
from src.database import database
from src.modules.group.models import GroupRequest, GroupUpdateRequest


async def get_group_by_id(groupId: int):
    return await database.group.find_first(where={"id": groupId})


async def get_group_by_code_and_subject_code_and_academicSchedulePensumId(
    code: int, subject_code: str, academicSchedulePensumId: int
):
    return await database.group.find_first(
        where={
            "code": code,
            "subject": {"code": subject_code},
            "academicSchedulePensumId": academicSchedulePensumId,
        }
    )


async def add_group(data: GroupRequest):
    return await database.group.create(data=data.model_dump())


async def add_group_base(data: GroupRequest):
    return await database.group.create(data=data)


async def update_group_by_id(groupId: int, data: GroupUpdateRequest):
    await database.group.update(
        where={"id": groupId},
        data={
            "groupSize": data.groupSize,
            "modality": data.modality,
            "maxSize": data.maxSize,
            "registeredPlaces": data.registeredPlaces,
        },
    )

    await update_group_proffesor(data.professors, groupId)


async def delete_group_by_id(groupId: int):
    return await database.group.delete(where={"id": groupId})


async def create_classroom_x_group(data):
    return await database.classroom_x_group.create(data=data)


async def get_groups_by_academic_schedule_id(academic_schedule_id: int) ->List[GroupResponse]:
    academic_schedules = await database.academic_schedule_pensum.find_many(
        where={"academicScheduleId": academic_schedule_id},
        include={
            "group": {
                "include": {
                    "classroom_x_group": {
                        "include": {
                            "mainClassroom": True,
                            "auxClassroom": True,
                        }
                    },
                    "group_x_professor": {"include": {"professor": True}},
                    "mirror_group": True,
                    "subject": {
                        "include": {"pensum": {"include": {"academic_program": True}}}
                    },
                }
            }
        },
    )
    groups = []
    for academic_schedule in academic_schedules:
        groups.extend(academic_schedule.group)
    return groups


async def get_all_groups_by_mirror_group_id(mirror_group_id: int):
    return await database.group.find_many(where={"mirrorGroupId": mirror_group_id})


async def get_group_by_id(groupId: int):
    return await database.group.find_first(where={"id": groupId})


async def get_groups_by_subjectId_and_academicSchedulePenusmId(
    subjectId: int, academicSchedulePensumId: int
):
    return await database.group.find_many(
        where={
            "subjectId": subjectId,
            "academicSchedulePensumId": academicSchedulePensumId,
        }
    )


async def soft_delete_group(groupId: int):
    return await database.group.update(
        where={"id": groupId},
        data={"code": 0, "groupSize": 0, "maxSize": 0, "registeredPlaces": 0},
    )


async def get_all_groups_by_schedule_pensum_id(schedule_pensum_ids: list[int]):
    return await database.group.find_many(
        where={
            "academicSchedulePensumId": {"in": schedule_pensum_ids},
        },
        include={
            "classroom_x_group": {
                "include": {
                    "mainClassroom": True,
                    "auxClassroom": True,
                }
            },
            "group_x_professor": {"include": {"professor": True}},
            "mirror_group": True,
            "subject": {"include": {"pensum": {"include": {"academic_program": True}}}},
        },
    )


async def exist_base_groups(schedule_pensum_id: int):
    return await database.group.find_first(
        where={"academicSchedulePensumId": schedule_pensum_id}
    )


async def updata_group_schedule(group_classroom_id: int, schedule: str):
    return await database.classroom_x_group.update(
        where={"id": group_classroom_id}, data={"mainSchedule": schedule}
    )
