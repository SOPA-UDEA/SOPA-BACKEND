from fastapi import APIRouter
from pydantic import BaseModel
from src.modules.subject.services import get_all_subjects, get_subjects_by_pensum_id


router = APIRouter( 
    tags=["subject"],
)


@router.get("/lists")
async def read_all_subjects():
    lists = await get_all_subjects()
    return {"subjects": lists}
    
@router.get("/by_pensum/{pensumId}")
async def read_subjects_by_pensum(pensumId: int):
    lists = await get_subjects_by_pensum_id(pensumId)
    return {"subjects": lists}