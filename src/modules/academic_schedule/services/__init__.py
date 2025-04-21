from src.database import database
import pandas as pd
from prisma import Prisma



async def get_all_academic_schedules():
    return await database.academic_schedule.find_many()

async def add_academic_schedule(data):
    return await database.academic_schedule.create(data=data)


