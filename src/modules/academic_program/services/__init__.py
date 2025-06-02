from src.database import database

async def get_all_academic_programs():
    return await database.academic_program.find_many()

async def get_program_by_id(id: int):
    return await database.academic_program.find_unique(where={'id': id})


