from src.database import database
from src.modules.classroom.models import Classroom, ClassroomRequest
from src.modules.group_classroom.services import get_group_classroom_by_main_classroom_id

async def get_classrooms() -> list[Classroom]:
    return await database.classroom.find_many()

async def create_classroom(classroom_request: ClassroomRequest) -> Classroom:
    classroom_data = await database.classroom.create(
        data=classroom_request.model_dump()
    )
    return Classroom.model_validate(classroom_data.model_dump())

async def update_classroom(
    classroom_id: int, classroom_request: ClassroomRequest
) -> Classroom:
    classroom_data = await database.classroom.update(
        where={"id": classroom_id},
        data=classroom_request.model_dump()
    )
    return Classroom.model_validate(classroom_data.model_dump())

async def delete_classroom(classroom_id: int) -> None:
    await database.classroom.delete(where={"id": classroom_id})

async def change_classroom_status(
    classroom_id: int, enable: bool
) -> Classroom:
    classroom_data = await database.classroom.update(
        where={"id": classroom_id},
        data={"enabled": enable}
    )
    return Classroom.model_validate(classroom_data.model_dump())

async def check_classroom_in_use(
    classroom_id: int
) -> bool:
    group_classroom = await get_group_classroom_by_main_classroom_id(classroom_id)
    return group_classroom is not None