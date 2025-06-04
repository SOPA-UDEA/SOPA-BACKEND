from src.database import database
from typing import BinaryIO
import pandas as pd
import gc
from fastapi import HTTPException
from src.modules.classroom.models import ClassroomRequest
from src.modules.classroom.services import create_classroom


async def upload_classrooms_from_excel(file: BinaryIO) -> dict:
    OWN_DEPARTMENT = "18"
    """
    Upload classrooms from an Excel file.
    """
    try:
        # Read Excel file
        df = pd.read_excel(file, engine='openpyxl', sheet_name="Sistemas")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error reading Excel file: {str(e)}")

    try:
        for _, row in df.iterrows():
            classrooms = str(row["AULA"]).strip() if pd.notnull(row["AULA"]) else None

            if classrooms is None:
                continue

            # Separating classrooms
            classrooms_list = [c.strip() for c in classrooms.split("|")]
            for classroom in classrooms_list:
                # Check if the classroom already exists in the database
                existing_classroom = await database.classroom.find_first(
                    where={"location": classroom}
                )
                if existing_classroom:
                    continue

                # Create a new ClassroomRequest object
                classroom_request = ClassroomRequest(
                    capacity=int(row["CUPO"]),
                    location=classroom,
                    ownDepartment=classroom.startswith(OWN_DEPARTMENT),
                    virtualMode=classroom in ("INGENIA", "UDE@"),
                    enabled=True,
                )

                # Create the classroom in the database
                await create_classroom(classroom_request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating classroom: {str(e)}")
    finally:
        del df
        gc.collect()

    return {"message": "Classrooms uploaded successfully"}
