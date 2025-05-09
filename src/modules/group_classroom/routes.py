
from fastapi import APIRouter
from fastapi import HTTPException
from fastapi import UploadFile, File
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from src.modules.group_classroom.services.upload_excel import upload_excel
from src.modules.group_classroom.services.check_collision import check_collision

router = APIRouter(
    tags=["group_classroom"],
)

@router.post("/upload-excel-drai")
async def upload_excel_drai(file: UploadFile = File(...)):
    try:
        # Call the upload_excel function to process the file
        await upload_excel(file.file)
        return JSONResponse(content={"message": "File processed successfully"}, status_code=200)
    except HTTPException as e:
        # Handle any HTTP exceptions raised during processing
        return JSONResponse(content=jsonable_encoder(e.detail), status_code=e.status_code)
    except Exception as e:
        # Handle any other exceptions that may occur
        return JSONResponse(content={"error": str(e)}, status_code=500)

@router.get("/collision")
async def check_collision_route():
    try:
        await check_collision()
        return JSONResponse(content={"message": "Collision check completed successfully"}, status_code=200)
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)
    