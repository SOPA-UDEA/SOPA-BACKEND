from fastapi import APIRouter
from pydantic import BaseModel, Field
from src.modules.academic_schedule.services import get_all_academic_schedules, add_academic_schedule

class AcademicScheduleRequest(BaseModel):
    semester: str = Field(min_length=4, max_length=150)

router = APIRouter( 
    tags=["academic_schedule"],
)

@router.get("/lists")
async def get_academic_schedules():
    academic_schedules = await get_all_academic_schedules()
    return  {"academic_schedules": academic_schedules}

@router.post("/create")
async def create_academic_schedule(academic_schedule_request: AcademicScheduleRequest):
    academic_schedule = await add_academic_schedule(academic_schedule_request.model_dump())
    return academic_schedule
    