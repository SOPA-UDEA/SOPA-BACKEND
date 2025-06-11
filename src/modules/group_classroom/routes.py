from fastapi import APIRouter
from fastapi import HTTPException
from fastapi import UploadFile, File, Form
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.encoders import jsonable_encoder
from src.modules.academic_schedule.models import ScheduleRequestDrai
from src.modules.group_classroom.models import CollisionRequest
from src.modules.group_classroom.services.upload_excel import upload_excel
from src.modules.group_classroom.services.update_excel import update_excel
from src.modules.group_classroom.services.export_excel import (
    export_group_classrooms_to_excel,
)
from src.modules.group_classroom.services.check_collision import check_collision
from src.modules.group_classroom.services import get_specific_group_classroom
from src.modules.group_classroom.services.check_mirror_group import check_mirror_group
from src.modules.group_classroom.services.check_schedule_or_classroom_modified import (
    check_schedule_or_classroom_modified,
)
from src.modules.group_classroom.services.check_capacity import check_capacity
from src.modules.group_classroom.services import find_group_classroom_by_id


router = APIRouter(
    tags=["group_classroom"],
)


@router.post("/upload-excel-drai")
async def upload_excel_drai(
    semester: str = Form(...), pensumId: int = Form(...), file: UploadFile = File(...)
):
    try:
        # Call the upload_excel function to process the file
        schedule_request = ScheduleRequestDrai(semester=semester, pensumId=pensumId)
        await upload_excel(file.file, schedule_request)
        return JSONResponse(
            content={"message": "File processed successfully"}, status_code=200
        )
    except HTTPException as e:
        # Handle any HTTP exceptions raised during processing
        return JSONResponse(
            content=jsonable_encoder(e.detail), status_code=e.status_code
        )
    except Exception as e:
        # Handle any other exceptions that may occur
        return JSONResponse(
            content={"detail": f"Error processing the file: {str(e)}"}, status_code=500
        )


@router.post("/update-excel-drai")
async def update_excel_route(
    semester: str = Form(...), pensumId: int = Form(...), file: UploadFile = File(...)
):
    try:
        # Create a ScheduleRequestDrai object from the form data
        schedule_request = ScheduleRequestDrai(semester=semester, pensumId=pensumId)
        # Call the update_excel function to process the file
        await update_excel(file.file, schedule_request)
        return JSONResponse(
            content={"message": "Excel updated successfully"}, status_code=200
        )
    except HTTPException as e:
        # Handle any HTTP exceptions raised during processing
        return JSONResponse(
            content=jsonable_encoder(e.detail), status_code=e.status_code
        )
    except Exception as e:
        # Handle any other exceptions that may occur
        return JSONResponse(
            content={"detail": f"Error processing the file: {str(e)}"}, status_code=500
        )


@router.post("/collision")
async def check_collision_route(request: CollisionRequest):
    try:
        await check_collision(request.semester)
        return JSONResponse(
            content={"message": "Collision check completed successfully"},
            status_code=200,
        )
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)


@router.get("/specific-group-classroom")
async def find_specific_group_classroom(group_id: int, skip: int = 0, take: int = 10):
    try:
        return await get_specific_group_classroom(group_id, skip, take)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/check-schedule-classroom-modified")
async def check_group_classroom_modified():
    try:
        await check_schedule_or_classroom_modified()
        return JSONResponse(
            content={
                "message": "Check schedule or classroom modified completed successfully"
            },
            status_code=200,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/check-capacity")
async def check_capacity_route():
    try:
        await check_capacity()
        return JSONResponse(
            content={"message": "Capacity check completed successfully"},
            status_code=200,
        )
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)


@router.get("/check-mirror-group")
async def check_mirror_group_route():
    try:
        await check_mirror_group()
        return JSONResponse(
            content={"message": "Mirror group check completed successfully"},
            status_code=200,
        )
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)


@router.get("/find-by-id/{id}")
async def find_by_id(id: int):
    try:
        group_classroom = await find_group_classroom_by_id(id)
        if not group_classroom:
            raise HTTPException(status_code=404, detail="Group Classroom not found")
        return group_classroom
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/export-excel", response_class=StreamingResponse)
async def export_group_classrooms_to_excel_route(scheduleRequest: ScheduleRequestDrai):
    try:
        response = await export_group_classrooms_to_excel(scheduleRequest)
        return response
    except HTTPException as e:
        return JSONResponse(
            content=jsonable_encoder(e.detail), status_code=e.status_code
        )
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)
