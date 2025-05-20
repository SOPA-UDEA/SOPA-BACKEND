from fastapi import APIRouter
from fastapi import HTTPException
from fastapi import UploadFile, File
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from src.modules.group_classroom.services.upload_excel import upload_excel
from src.modules.group_classroom.services.update_excel import update_excel
from src.modules.group_classroom.services.check_collision import check_collision
from src.modules.group_classroom.services import get_specific_group_classroom

router = APIRouter(
    tags=["group_classroom"],
)


@router.post("/upload-excel-drai")
async def upload_excel_drai(file: UploadFile = File(...)):
    try:
        # Call the upload_excel function to process the file
        await upload_excel(file.file)
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
        return JSONResponse(content={"error": str(e)}, status_code=500)


@router.post("/update-excel-drai")
async def update_excel_route(file: UploadFile = File(...)):
    try:
        # Call the update_excel function to process the file
        await update_excel(file.file)
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
        return JSONResponse(content={"error": str(e)}, status_code=500)


@router.get("/collision")
async def check_collision_route():
    try:
        await check_collision()
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
