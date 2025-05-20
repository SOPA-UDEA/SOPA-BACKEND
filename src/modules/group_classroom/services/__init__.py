from src.database import database
from src.modules.group_classroom.models import (
    GroupClassroomRequest,
    MessageGroupClassroomRequest,
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


async def get_all_group_classrooms():

    return await database.classroom_x_group.find_many(
        include={
            "classroom_classroom_x_group_mainClassroomIdToclassroom": True,
            "group": True,
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
