from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from starlette import status

from src.modules.professor.services import get_all_professors

router = APIRouter( 
    tags=["professor"],
)

class AcademicScheduleRequest(BaseModel):
    semester: str = Field(min_length=4, max_length=150)

class Professor(BaseModel):
    id: int
    name: str
    identification: str

@router.get("/lists", status_code=status.HTTP_200_OK, response_model=list[Professor])
async def get_professors():
    professors = await get_all_professors()
    if not professors:
        raise HTTPException(status_code=404, detail="No professors found")
    return professors
