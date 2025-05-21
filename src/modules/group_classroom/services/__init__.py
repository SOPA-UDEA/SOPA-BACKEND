from src.database import database
from typing import List
from src.modules.group_classroom.models import (
    GroupClassroomRequest,
    MessageGroupClassroomRequest,
    GroupClassroomRequestAux,
    GroupClassroomResponse,
)


async def get_group_classroom_by_main_classroom_id_and_group_id_and_main_schedule(
    main_classroom_id: int, group_id: int, main_schedule: str
):
    return await database.classroom_x_group.find_first(
        where={
            "mainClassroomId": main_classroom_id,
            "groupId": group_id,
            "mainSchedule": main_schedule,
        }
    )


async def add_group_classroom(data: GroupClassroomRequest):
    return await database.classroom_x_group.create(data=data.model_dump())


async def get_classrooms_and_schedules(main_classroom_id: int, days: list[str]):
    return await database.classroom_x_group.find_many(
        where={
            "mainClassroomId": main_classroom_id,
            "AND": [{"mainSchedule": {"contains": day}} for day in days],
        },
        include={
            "classroom_classroom_x_group_mainClassroomIdToclassroom": True,
        },
    )


async def get_all_group_classrooms() -> List[GroupClassroomResponse]:

    return await database.classroom_x_group.find_many()


async def get_specific_group_classroom(group_id: int, skip: int, take: int):
    return await database.classroom_x_group.find_many(
        where={
            "groupId": group_id,
        },
        skip=skip,
        take=take,
        order={
            "id": "asc",
        },
    )


async def add_message_group_classroom(data: MessageGroupClassroomRequest):
    return await database.message_classroom_group.create(data=data.model_dump())


async def get_message_group_classroom(
    group_id: int,
    message_type: int,
):
    return await database.message_classroom_group.find_first(
        where={
            "groupId": group_id,
            "messageTypeId": message_type,
        }
    )


async def update_group_classroom_aux(
    group_classroom_id: int, data: GroupClassroomRequestAux
):
    return await database.classroom_x_group.update(
        where={
            "id": group_classroom_id,
        },
        data=data.model_dump(),
    )


async def get_group_classroom_by_group_id(group_id: int):
    return await database.classroom_x_group.find_many(
        where={
            "groupId": group_id,
        },
        order={
            "id": "asc",
        },
    )

async def update_group_classroom(
    group_classroom_id: int, data: GroupClassroomRequest
):
    return await database.classroom_x_group.update(
        where={
            "id": group_classroom_id,
        },
        data=data.model_dump(),
    )