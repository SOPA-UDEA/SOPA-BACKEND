from typing import Any, Dict, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Json
from src.modules.subject.services import get_all_subjects, get_subjects_by_pensum_id
from starlette import status

router = APIRouter( 
    tags=["subject"],
)

class prerequisiteResponse(BaseModel):
    id:int
    code:str
    subjectId:int

class SubjectResponse(BaseModel):
    id: int
    name: str
    level: int
    fields: Dict[str, Any]
    code: str
    credits: int
    weeklyHours: int
    weeks: int
    validable: bool
    enableable: bool
    coRequirements: str
    creditRequirements: Optional[str]
    pensumId: int
    prerequirement: Optional[list[prerequisiteResponse]]

# @router.get("/lists",status_code=status.HTTP_200_OK ,response_model=list[SubjectResponse])
# async def read_all_subjects():
#     subjects = await get_all_subjects()
#     if subjects is not None:
#         return subjects
#     raise HTTPException(status_code=404, detail="No subjects found")
    
@router.get("/by_pensum/{pensumId}",status_code=status.HTTP_200_OK, response_model=list[SubjectResponse])
async def read_subjects_by_pensum(pensumId: int):
    subjects = await get_subjects_by_pensum_id(pensumId)
    if subjects is not None:
        return subjects
    raise HTTPException(status_code=404, detail="No subjects found")