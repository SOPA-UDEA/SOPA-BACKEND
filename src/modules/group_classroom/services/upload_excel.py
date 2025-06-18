from typing import BinaryIO
import random
import string
import gc
import pandas as pd
from fastapi import HTTPException
from src.modules.mirror_group.services import create_mirror_group
from src.modules.subject.services import get_subject_by_code
from src.modules.group.services import (
    get_group_by_code_and_subject_code_and_academicSchedulePensumId,
    add_group,
)
from src.modules.group_classroom.helpers import (
    get_or_create_pensum_and_academic_schedule_pensum_id,
    create_professors_for_group,
)
from src.modules.group_classroom.services import (
    get_group_classroom_by_main_classroom_id_and_group_id_and_main_schedule,
    add_group_classroom,
)
from src.modules.academic_schedule.models import (
    ScheduleRequestDrai,
)
from src.modules.group.models import GroupRequest
from src.modules.classroom.services import get_classroom_by_location
from src.modules.group_classroom.models import GroupClassroomRequest


async def upload_excel(file: BinaryIO, schedule_request: ScheduleRequestDrai):
    try:
        # Read the Excel file into a DataFrame
        df = pd.read_excel(file, engine="openpyxl")

    except Exception as e:
        # Handle the case where the file is not a valid Excel file
        raise HTTPException(
            status_code=400, detail=f"Error reading Excel file: {str(e)}"
        )

    # get semester and pensumId from the request
    try:
        semester = schedule_request.semester
        pensum_id = schedule_request.pensumId
        pensum, academic_schedule_pensum_id = (
            await get_or_create_pensum_and_academic_schedule_pensum_id(
                semester, pensum_id
            )
        )

        # iter ate over the rows of the DataFrame and insert them into the database
        for _, row in df.iterrows():
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
            group = (
                await get_group_by_code_and_subject_code_and_academicSchedulePensumId(
                    group_code, subject_code, academic_schedule_pensum_id.id
                )
            )
            if not group:
                iniciales = "".join([p[0] for p in subject.name.split()])
                mirror_group_name = iniciales + "".join(
                    random.choices(string.ascii_letters + string.digits, k=5)
                )
                mirror_group = await create_mirror_group({"name": mirror_group_name})

                # If the group does not exist, create it
                new_group = GroupRequest(
                    code=group_code,
                    groupSize=int(row["CUPO"]),
                    modality=pensum.academic_program.modalityAcademic,
                    subjectId=subject.id,
                    academicSchedulePensumId=academic_schedule_pensum_id.id,
                    mirrorGroupId=mirror_group.id,
                    maxSize=int(row["CUPO"]),
                    registeredPlaces=int(row["CUPO"]),
                )
                group = await add_group(new_group)
            # get the professors an their identifications
            professors = (
                str(row["PROFESOR(ES)"]).strip()
                if pd.notnull(row["PROFESOR(ES)"])
                else None
            )
            identifications = (
                str(row["IDENTIFICACION"]).strip()
                if pd.notnull(row["IDENTIFICACION"])
                else None
            )
            if professors and identifications:
                identifications_list = [i.strip() for i in identifications.split("|")]
                professors_list = [p.strip() for p in professors.split("|")]
                await create_professors_for_group(
                    professors_list, identifications_list, group.id
                )
            # get the classrooms and schedules
            classrooms = str(row["AULA"]).strip() if pd.notnull(row["AULA"]) else None

            schedules = (
                str(row["HORARIO"]).strip() if pd.notnull(row["HORARIO"]) else None
            )
            if not classrooms or not schedules:
                continue  # skip if there are no classrooms or schedules

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
                # remove whitespace from individual schedules
                individual_schedule = [
                    s.strip() for s in individual_schedule if s.strip()
                ]

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
                        classroom_x_group = await add_group_classroom(
                            new_classroom_x_group
                        )
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error processing Excel file: {str(e)}"
        )
