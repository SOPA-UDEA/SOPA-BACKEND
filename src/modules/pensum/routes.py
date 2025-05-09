from fastapi import APIRouter
from pydantic import BaseModel
from src.modules.pensum.services import get_all_pensums


router = APIRouter( 
    tags=["pensum"],
)


@router.get("/lists")
async def read_all_pensum():
    lists = await get_all_pensums()
    return {"pensums": lists}
    
