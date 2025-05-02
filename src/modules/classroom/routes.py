from typing import List
from fastapi import APIRouter
from src.modules.classroom.models import ClassroomRequest
from src.modules.classroom.services import (
    get_classrooms,
    add_classroom,
    get_classroom_by_location,
)


router = APIRouter(
    tags=["classroom"],
)


@router.get("/lists")
async def create_group_list():
    lists = await get_classrooms()
    return {"classrooms available": lists}


@router.get("/location/{location}")
async def find_classroom_by_location(location: str):
    classroom = await get_classroom_by_location(location)
    if classroom:
        return classroom
    return {"error": "Classroom not found"}


@router.post("/create")
async def create_classroom(classroom: ClassroomRequest):
    classroom = await add_classroom(classroom)
    return classroom
