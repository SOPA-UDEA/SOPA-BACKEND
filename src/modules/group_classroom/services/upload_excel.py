from typing import BinaryIO
import gc
import pandas as pd
from fastapi import HTTPException
from src.modules.subject.services import get_subject_by_code
from src.modules.group.services import get_group_by_code_and_subject_code, add_group
from src.modules.group_classroom.services import (
    get_group_classroom_by_main_classroom_id_and_group_id_and_main_schedule,
    add_group_classroom,
)
from src.modules.group.models import GroupRequest
from src.modules.classroom.services import get_classroom_by_location
from src.modules.group_classroom.models import GroupClassroomRequest


async def upload_excel(file: BinaryIO):

    try:
        # Read the Excel file into a DataFrame
        df = pd.read_excel(file, engine="openpyxl")

    except Exception as e:
        # clean up memory
        del df
        gc.collect()
        # Handle the case where the file is not a valid Excel file
        raise HTTPException(
            status_code=400, detail=f"Error reading Excel file: {str(e)}"
        )

    # iter ate over the rows of the DataFrame and insert them into the database
    for _, row in df.iterrows():
        classrooms = str(row["AULA"]).strip() if pd.notnull(row["AULA"]) else None
        if not classrooms:
            # If there are no classrooms, skip this row
            continue
        # Get the subject code from the row
        faculty = str(row["FAC"]).zfill(2)
        department = str(row["DEP"]).zfill(2)
        subject = str(row["MAT"]).zfill(3)
        subject_code = f"{faculty}{department}{subject}"

        # Get the subject from database
        subject = await get_subject_by_code(subject_code)
        if not subject:
            # clean up memory
            del df
            gc.collect()
            # Handle the case where the subject code is not found in the database
            raise HTTPException(
                status_code=400,
                detail=f"Subject code {subject_code} not found in the database",
            )

        group_code = int(row["GR"])

        # Search for the group in the database
        group = await get_group_by_code_and_subject_code(group_code, subject_code)
        if not group:
            # If the group does not exist, create it
            new_group = GroupRequest(
                code=group_code,
                groupSize=int(row["CUPO"]),
                modality="PRESENCIAL",
                subjectId=subject.id,
                academicSchedulePensumId=4,
                mirrorGroupId=None,
                maxSize=int(row["CUPO"]),
                registeredPlaces=int(row["CUPO"]),
            )
            group = await add_group(new_group)

        schedules = str(row["HORARIO"]).strip() if pd.notnull(row["HORARIO"]) else None
        # separate the classrooms by |
        classrooms_list = [c.strip() for c in classrooms.split("|")]
        # separate the schedules by |
        schedules_block = [s.strip() for s in schedules.split("|")]

        for i, classroom in enumerate(classrooms_list):
            # check if there are enough schedules for the classrooms
            if i >= len(schedules_block):
                raise HTTPException(
                    status_code=400,
                    detail=f"Not enough schedules for classrooms in group {group_code}",
                )
            schedule_block = schedules_block[i]
            individual_schedule = schedule_block.split(" ")

            # get the schedules for each classroom
            for schedule in individual_schedule:
                # search for the classroom in the database
                classroom_data = await get_classroom_by_location(classroom)
                if not classroom_data:
                    # raise exception if the classroom does not exist in the database
                    raise HTTPException(
                        status_code=400,
                        detail=f"Classroom {classroom} not found in the database",
                    )
                # check if classroom_x_group exists in the database
                classroom_x_group = await get_group_classroom_by_main_classroom_id_and_group_id_and_main_schedule(
                    main_classroom_id=classroom_data.id,
                    group_id=group.id,
                    main_schedule=schedule,
                )

                if not classroom_x_group:
                    # create the classroom_x_group in the database
                    new_classroom_x_group = GroupClassroomRequest(
                        mainClassroomId=classroom_data.id,
                        groupId=group.id,
                        mainSchedule=schedule,
                    )
                    classroom_x_group = await add_group_classroom(new_classroom_x_group)
