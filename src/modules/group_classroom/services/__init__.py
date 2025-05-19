from src.database import database

async def get_group_classroom_by_main_classroom_id(
    main_classroom_id: int,
):
    return await database.classroom_x_group.find_first(
        where={
            "mainClassroomId": main_classroom_id,
        }
    )