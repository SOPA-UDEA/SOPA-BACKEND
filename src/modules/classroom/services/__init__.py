from src.database import database

async def get_classrooms() -> list:

    return await database.classroom.find_many()

