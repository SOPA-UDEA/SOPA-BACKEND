from src.database import database

from src.modules.academic_schedule.models import AcademicSchedulePensumIdRequest


async def get_all_schedules():
    return await database.academic_schedule.find_many()


async def add_schedule(data):
    return await database.academic_schedule.create(data=data)


async def delete_schedule(academic_schedule_id):
    return await database.academic_schedule.delete(where={"id": academic_schedule_id})


async def get_schedule_by_id(academic_schedule_id):
    return await database.academic_schedule.find_first(
        where={"id": academic_schedule_id}
    )


async def get_schedule_by_semester(semester: str):
    return await database.academic_schedule.find_first(where={"semester": semester})


async def get_academic_schedule_pensum_id(
    academic_schedule_pensum_id_request: AcademicSchedulePensumIdRequest,
):
    return await database.academic_schedule_pensum.find_first(
        where={
            "academicScheduleId": academic_schedule_pensum_id_request.academicScheduleId,
            "pensumId": academic_schedule_pensum_id_request.pensumId,
        }
    )


async def add_academic_schedule_pensum_id(
    academic_schedule_pensum_id_request: AcademicSchedulePensumIdRequest,
):
    return await database.academic_schedule_pensum.create(
        data=academic_schedule_pensum_id_request.model_dump()
    )
