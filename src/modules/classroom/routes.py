from typing import List
from fastapi import APIRouter, File, UploadFile
from src.modules.classroom.models import Classroom, ClassroomRequest
from src.modules.classroom.services import get_classrooms, create_classroom, update_classroom, delete_classroom
from src.modules.classroom.services.upload_classrooms import upload_classrooms_from_excel
from fastapi.responses import JSONResponse
from fastapi.responses import Response
from fastapi import HTTPException

router = APIRouter(
    tags=["classroom"],
)

@router.get("/list")
async def get_classroom_list():
    """
    Get a list of classrooms.
    """
    try:
        classrooms = await get_classrooms()
        return classrooms 
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/create")
async def create_classroomReClassroomRequest_endpoint(classroom_request: ClassroomRequest):
    """
    Create a new classroom.
    """
    try:
        return await create_classroom(classroom_request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/upload", status_code=201)
async def upload_classrooms(file: UploadFile = File(...)):
    """
    Upload classrooms from an Excel file.
    """
    try:
        await upload_classrooms_from_excel(file.file)
        return JSONResponse(content={"message": "Classrooms uploaded successfully"}, status_code=201)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/update/{classroom_id}", response_model=Classroom, status_code=200)
async def update_classroom_endpoint(classroom_id: int, classroom_request: ClassroomRequest):
    """
    Update an existing classroom.
    """
    try:
        return await update_classroom(classroom_id, classroom_request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/delete/{classroom_id}", status_code=204)
async def delete_classroom_endpoint(classroom_id: int):
    """
    Delete a classroom.
    """
    try:
        await delete_classroom(classroom_id)
        return Response(status_code=204)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))