from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from src.modules.pensum.services import get_all_pensums
from starlette import status

router = APIRouter( 
    tags=["pensum"],
)

class Pensum(BaseModel):
    id: int
    version: int
    academicProgramId: int


@router.get("/lists", status_code=status.HTTP_200_OK, response_model=list[Pensum])
async def read_all_pensum():
    pensums = await get_all_pensums()
    if pensums is not None:
        return pensums
    raise HTTPException(status_code=404, detail="No pensum found")