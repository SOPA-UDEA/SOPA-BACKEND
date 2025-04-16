

from typing import List
from fastapi import APIRouter
from pydantic import BaseModel
from src.modules.classroom.services import get_classrooms




router = APIRouter(
    tags=["classroom"],
)

@router.get("/lists")
async def create_group_list():
    lists = await get_classrooms()
    return {"classrooms available": lists}