from src.database import database
from src.modules.classroom.models import Classroom, ClassroomRequest

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

async def disable_classroom(classroom_id: int) -> Classroom:
    classroom_data = await database.classroom.update(
        where={"id": classroom_id},
        data={"enabled": False}
    )
    return Classroom.model_validate(classroom_data.model_dump())