from src.database import database

async def get_classroom_and_schedules(classroomId: int, days: list[str]):
    return await database.classroom_x_group.find_many(
        where={
            "classroomId": classroomId,
            "AND": [
                { "schedule": {"contains": day}}
                for day in days
            ],
        },
        include={
            "classroom": True,
        }

    )

async def get_group_classroom(classroomId: int, groupId: int, schedule: str):
    return await database.classroom_x_group.find_first(
        where={
            "classroomId": classroomId,
            "groupId": groupId,
            "schedule": schedule,
        },
    )

