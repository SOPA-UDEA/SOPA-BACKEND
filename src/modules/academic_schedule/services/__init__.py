from src.database import database

async def get_all_academic_schedules():
    return await database.academic_schedule.find_many()

async def add_academic_schedule(data):
    return await database.academic_schedule.create(data=data)

async def delete_academic_schedule(academic_schedule_id):
    return await database.academic_schedule.delete(where={"id": academic_schedule_id})

async def get_academic_schedule_by_id(academic_schedule_id):
    return await database.academic_schedule.find_first(where={"id": academic_schedule_id})
