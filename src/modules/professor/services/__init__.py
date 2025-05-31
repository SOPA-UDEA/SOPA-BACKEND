from src.database import database

async def get_all_professors():
    return await database.professor.find_many() 
