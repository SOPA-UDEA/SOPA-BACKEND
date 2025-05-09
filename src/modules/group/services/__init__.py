import json
from src.database import database
from src.modules.group.models import GroupRequest


async def get_all_groups():
    return await database.group.find_many()


async def get_group_by_code_and_subject_code(code: int, subject_code: str):
    return await database.group.find_first(
        where={"code": code, "subject": {"code": subject_code}}
    )


async def add_group(data: GroupRequest):
    return await database.group.create(data=data.model_dump())


async def update_group_by_id(groupId: int, data):
    return await database.group.update(where={"id": groupId}, data=data)


async def delete_group_by_id(groupId: int):
    return await database.group.delete(where={"id": groupId})


async def create_academic_schedule_pesnum(data):
    return await database.academic_schedule_pensum.create(data=data)


async def get_academic_schedule_pensum_by_pensum_id_and_academic_schedule_id(
    pensum_id: int, academic_schedule_id: int
):
    return await database.academic_schedule_pensum.find_first(
        where={"pensumId": pensum_id, "academicScheduleId": academic_schedule_id}
    )

async def get_all_groups_by_mirror_group_id(mirror_group_id: int):
    return await database.group.find_many(
        where={"mirrorGroupId": mirror_group_id}
    )

async def get_group_by_id(groupId: int):
    return await database.group.find_first(where={"id": groupId})