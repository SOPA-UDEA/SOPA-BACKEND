from typing import List
from fastapi import APIRouter, File, UploadFile
from src.modules.group_classroom.services import upload_classroom_x_group, get_classroom_and_schedules
from src.modules.group_classroom.models import ClassroomSchedulesRequest
from fastapi import HTTPException
from fastapi.responses import JSONResponse

router = APIRouter(
    tags=["group_classroom"],
)

@router.post("/upload-excel/")
async def upload_excel(file: UploadFile = File(...)):
    try:
        if file.filename.endswith(".xlsx"):
            await upload_classroom_x_group(file.file)
            return JSONResponse(status_code=200, content={"message": "File uploaded successfully"})
        else:
            raise HTTPException(status_code=400, detail="Invalid file format. Only .xlsx files are allowed.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing the file: {e}")

@router.post("/classroom-and-schedules/")
async def find_classroom_and_schedules(request: ClassroomSchedulesRequest):
    try:
        classroom = await get_classroom_and_schedules(classroomId=request.classroomId, days=request.days)
        return classroom
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"{e}")
