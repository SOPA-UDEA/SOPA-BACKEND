

from typing import List
from fastapi import APIRouter
from pydantic import BaseModel



router = APIRouter(
    tags=["group"],
)

@router.get("/lists")
async def create_group_list():
    return {"group": "This is a group list"}