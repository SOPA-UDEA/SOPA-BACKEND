from fastapi import APIRouter
from pydantic import BaseModel, Field
from src.modules.academic_program.services import get_all_academic_programs


router = APIRouter( 
    tags=["academic_program"],
)

@router.get("/lists")
async def get_academic_programs():
    academic_program = await get_all_academic_programs()
    return  {"academic_program": academic_program}

    