from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from src.modules.academic_schedule.services import get_all_academic_schedules, add_academic_schedule, delete_academic_schedule
from starlette import status



router = APIRouter( 
    tags=["academic_schedule"],
)

class AcademicScheduleRequest(BaseModel):
    semester: str = Field(min_length=4, max_length=150)

class AcademicScheduleResponse(BaseModel):
    id: int
    semester: str

@router.get("/lists", status_code=status.HTTP_200_OK, response_model=list[AcademicScheduleResponse])
async def get_academic_schedules():
    academic_schedules = await get_all_academic_schedules()
    if not academic_schedules:
        raise HTTPException(status_code=404, detail="No academic schedules found")
    return academic_schedules

@router.post("/create", status_code=status.HTTP_201_CREATED, response_model=AcademicScheduleResponse)
async def create_academic_schedule(academic_schedule_request: AcademicScheduleRequest):
    academic_schedule = await add_academic_schedule(academic_schedule_request.model_dump())
    if not academic_schedule:
        raise HTTPException(status_code=400, detail="Failed to create academic schedule")
    return academic_schedule  
    
@router.delete("/delete/{academic_schedule_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_academic_schedule_by_id(academic_schedule_id: int):
    academic_schedule = await delete_academic_schedule(academic_schedule_id)
    if not academic_schedule:
        raise HTTPException(status_code=404, detail="Academic schedule not found")
    return {"detail": "Academic schedule deleted successfully"}