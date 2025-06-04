from src.database import database
from prisma import Prisma



async def get_all_academic_programs():
    return await database.academic_program.find_many()



