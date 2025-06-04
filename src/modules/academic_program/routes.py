from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from src.modules.academic_program.services import get_all_academic_programs
from starlette import status

router = APIRouter( 
    tags=["academic_program"],
)

class AcademicProgramResponse(BaseModel):
    id: int 
    name: str 
    code: str 
    modalityAcademic: str 
    headquarter: str 
    version: int 
    modalityId: int 
    facultyId: int 
    departmentId: int 

@router.get("/lists", status_code=status.HTTP_200_OK, response_model=list[AcademicProgramResponse])
async def get_academic_programs():
    academic_programs = await get_all_academic_programs()
    if not academic_programs:
        raise HTTPException(status_code=404, detail="No academic programs found")
    return  academic_programs

    