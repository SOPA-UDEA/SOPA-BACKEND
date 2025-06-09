from src.database import database

async def get_schedule_x_pensum_by_pensum_id_and_schedule_id(
    pensum_id: int, schedule_id: int
):
    return await database.academic_schedule_pensum.find_first(
        where={"pensumId": pensum_id, "academicScheduleId": schedule_id}
    )

async def create_schedule_pensum(data):
    return await database.academic_schedule_pensum.create(data=data)

async def get_schedule_pensum_by_pensum_id_and_schedule_id(pensum_id: int, schedule_id: int):
    return await database.academic_schedule_pensum.find_first(where={"pensumId": pensum_id, "academicScheduleId": schedule_id})

async def get_all_schedule_pensum_by_schedule_and_pensum(pensums_id: list[int], schedule_id: int):
    return await database.academic_schedule.find_many(
        where={
            'pensumId': {'in': pensums_id},
            'academicScheduleId': schedule_id
        }
    )