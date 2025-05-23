from typing import BinaryIO
import gc
import pandas as pd
from fastapi import HTTPException
from src.modules.subject.services import get_subject_by_code
from src.modules.group.services import get_group_by_code_and_subject_code
from src.modules.group_classroom.services import (
    update_group_classroom_aux,
    get_group_classroom_by_group_id,
    update_group_classroom,
    add_message_group_classroom
)
from src.modules.classroom.services import get_classroom_by_location
from src.modules.group_classroom.models import (
    GroupClassroomRequestAux,
    GroupClassroomRequest,
    GroupClassroomResponse,
    MessageGroupClassroomRequest
)


async def update_excel(file: BinaryIO):
    CLASSROOMS_NOT_DEFINED = (1, 2, 3)

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
    group_classroom_pointer = {}  # Track progress for each group.id
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
            del df
            gc.collect()
            # Handle the case where the group code is not found in the database
            raise HTTPException(
                status_code=400,
                detail=f"Group code {group_code} not found in the database",
            )
        # Check if the group has already been processed
        if group.id not in group_classroom_pointer:
            group_classrooms = await get_group_classroom_by_group_id(group.id)
            if not group_classrooms:
                del df
                gc.collect()
                # Handle the case where the group classrooms are not found in the database
                raise HTTPException(
                    status_code=400,
                    detail=f"Group classrooms for group {group.id} not found in the database",
                )
            group_classroom_pointer[group.id] = {
                "group_classrooms": group_classrooms,
                "index": 0,
            }
        group_data = group_classroom_pointer[group.id]
        group_classrooms = group_data["group_classrooms"]
        pointer = group_data["index"]

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
            for j, schedule in enumerate(individual_schedule):

                index = pointer + i + j
                if index >= len(group_classrooms):
                    # clean up memory
                    del df
                    gc.collect()
                    # Handle the case where there are more classrooms than group classrooms
                    raise HTTPException(
                        status_code=400,
                        detail=f"Not enough group classrooms for group {group.id}",
                    )
                # search for the classroom in the database
                classroom_data = await get_classroom_by_location(classroom)
                if not classroom_data:
                    # raise exception if the classroom does not exist in the database
                    raise HTTPException(
                        status_code=400,
                        detail=f"Classroom {classroom} not found in the database",
                    )
                # check if classroom_x_group exists in the database
                classroom_x_group: GroupClassroomResponse = group_classrooms[index]
                print(f"classroom_x_group: {classroom_x_group}")
                # This ids mean that the group does not have a main classroom set
                if classroom_x_group.mainClassroomId in CLASSROOMS_NOT_DEFINED:
                    # update the main classroom for the group classroom
                    update_data = GroupClassroomRequest(
                        groupId=classroom_x_group.groupId,
                        mainClassroomId=classroom_data.id,
                        mainSchedule=classroom_x_group.mainSchedule,
                        auxSchedule=schedule,
                        auxClassroomId=classroom_data.id,
                    )
                    await update_group_classroom(
                        group_classroom_id=classroom_x_group.id, data=update_data
                    )
                    # add message to the database
                    message = MessageGroupClassroomRequest(
                        groupId=classroom_x_group.groupId,
                        messageTypeId=3,
                        detail=f'Classroom {classroom} set ',
                    )
                    await add_message_group_classroom(message)
                    continue

                # update the classroom_x_group with the new classroom and schedule
                update_data = GroupClassroomRequestAux(
                    auxClassroomId=classroom_data.id,
                    auxSchedule=schedule,
                )
                await update_group_classroom_aux(
                    group_classroom_id=classroom_x_group.id, data=update_data
                )
        # update the pointer for the next iteration
        group_classroom_pointer[group.id]["index"] += 1
