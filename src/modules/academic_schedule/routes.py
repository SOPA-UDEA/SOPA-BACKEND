from fastapi import APIRouter, HTTPException
from src.modules.academic_schedule.models import ScheduleRequest, ScheduleResponse, ScheduleCreateResponse
from src.modules.academic_schedule.services import add_schedule, delete_schedule, get_schedule_by_id, get_schedule_by_semester
from src.modules.schedule_x_group.services import get_schedule_pensum_by_pensum_id_and_schedule_id,  create_schedule_pensum
from starlette import status



router = APIRouter( 
    tags=["academic_schedule"],
)



@router.post("/create", status_code=status.HTTP_201_CREATED, response_model=ScheduleCreateResponse)
async def create_schedule(schedule_request: ScheduleRequest):
    try:
        pensumsIds = schedule_request.pensumsIds
        schedule_pensum_ids = []
        schedule = await get_schedule_by_semester(schedule_request.semester)
        if not schedule:
            scheduleCreate = {
                'semester': schedule_request.semester
            }
            schedule = await add_schedule(scheduleCreate)
        for pensum_id in pensumsIds:
            data = {
                'pensumId': pensum_id,
                'academicScheduleId': schedule.id
            }
            schedule_pensum = await get_schedule_pensum_by_pensum_id_and_schedule_id(pensum_id, schedule.id)
            if not schedule_pensum:
                schedule_pensum = await create_schedule_pensum(data)
            schedule_pensum_ids.append(schedule_pensum.id)
        response = {
            'id': schedule.id,
            'semester': schedule.semester,
            'schedule_pensum_ids': schedule_pensum_ids
        }
        return response
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
@router.delete("/delete/{schedule_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_schedule_by_id(schedule_id: int):
    schedule = await delete_schedule(schedule_id)
    if not schedule:
        raise HTTPException(status_code=404, detail="schedule not found")
    return {"detail": "schedule deleted successfully"}

@router.get("/schedule/{schedule_id}", status_code=status.HTTP_200_OK, response_model=ScheduleResponse)
async def get_schedule(schedule_id: int):
    schedule = await get_schedule_by_id(schedule_id)
    if not schedule:
        raise HTTPException(status_code=404, detail="schedule not found")
    return schedule

@router.get("/schedule/{schedule_semester}/{pensumId}", status_code=status.HTTP_200_OK)
async def get_schedule_pensum_by_name_and_pensum_id(schedule_semester: str, pensumId: int):
    schedule = await get_schedule_by_semester(schedule_semester)
    schedule_pensum = await get_schedule_pensum_by_pensum_id_and_schedule_id(pensumId, schedule.id)
    if not schedule_pensum:
        raise HTTPException(status_code=404, detail="schedule not found")
    return schedule_pensum

@router.get("/semester/{semester}", status_code=status.HTTP_200_OK, response_model=ScheduleResponse)
async def get_schedule_by_semester_route(semester: str):
    schedule = await get_schedule_by_semester(semester)
    if not schedule:
        raise HTTPException(status_code=404, detail="schedule not found")
    return schedule