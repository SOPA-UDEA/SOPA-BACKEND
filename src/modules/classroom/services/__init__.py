from src.database import database
from src.modules.classroom.models import ClassroomRequest

async def get_classrooms() -> list:

    return await database.classroom.find_many()

async def add_classroom(classroom: ClassroomRequest):
    return await database.classroom.create(data=classroom.model_dump())

async def get_classroom_by_location(location: str):
    return await database.classroom.find_first(where={"location": location})

