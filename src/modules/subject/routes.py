from fastapi import APIRouter, HTTPException
from src.modules.subject.services import get_all_subjects, get_subjects_by_pensum_id


router = APIRouter( 
    tags=["subject"],
)

@router.get("/lists")
async def read_all_subjects():
    subjects = await get_all_subjects()
    if subjects is not None:
        return subjects
    raise HTTPException(status_code=404, detail="No subjects found")
    
@router.get("/by_pensum/{pensumId}")
async def read_subjects_by_pensum(pensumId: int):
    subjects = await get_subjects_by_pensum_id(pensumId)
    if subjects is not None:
        return subjects
    raise HTTPException(status_code=404, detail="No subjects found")