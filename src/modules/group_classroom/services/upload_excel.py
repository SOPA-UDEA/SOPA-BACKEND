from typing import BinaryIO
import gc
import pandas as pd
from src.database import database
from src.modules.classroom.services import get_classroom_by_location, add_classroom
from src.modules.group.services import get_group_by_code_and_subject_code, add_group
from src.modules.group.models import GroupRequest
from src.modules.subject.services import get_subject_by_code, create_subject
from src.modules.subject.models import SubjectRequest
from src.modules.classroom.models import ClassroomRequest
from src.modules.group_classroom.services import (
    get_group_classroom,
    get_classroom_and_schedules,
)
from fastapi import HTTPException


async def upload_classroom_x_group(file: BinaryIO):

    df = pd.read_excel(file, engine="openpyxl")

    for index, row in df.iterrows():
        # Get the subject code from the row
        faculty = str(row["FAC"]).zfill(2)
        department = str(row["DEP"]).zfill(2)
        subject = str(row["MAT"]).zfill(3)
        subject_code = f"{faculty}{department}{subject}"

        # check if subject exists
        subject_data = await get_subject_by_code(code=subject_code)
        if subject_data is None:
            # create subject
            new_subject = SubjectRequest(
                level=1,
                fields={"1": 1},
                code=subject_code,
                credits=4,
                weeklyHours=4,
                weeks=16,
                enableable=False,
                validable=False,
                preRequirements=None,
                coRequirements=None,
                creditRequirements=None,
                name=str(row["NOMBRE MATERIA"]).strip(),
                pensumId=1,
            )
            subject_data = await create_subject(data=new_subject)
            print(f"Subject {subject_code} created.")

        # check if group exists
        group_data = await get_group_by_code_and_subject_code(
            code=int(row["GR"]), subject_code=subject_code
        )
        if group_data is None:
            # create group
            new_group = GroupRequest(
                code=int(row["GR"]),
                groupSize=int(row["CUPO"]),
                modality="PRESENCIAL",
                subjectId=subject_data.id,
                mirrorGroupId=2,
                academicScheduleId=1,
            )
            group_data = await add_group(data=new_group)

        classrooms = str(row["AULA"]).strip() if pd.notnull(row["AULA"]) else None
        schedules = str(row["HORARIO"]).strip() if pd.notnull(row["HORARIO"]) else None

        if not classrooms:
            continue

        # separating classrooms
        classroom_list = [c.strip() for c in classrooms.split("|")]
        # separating schedules
        schedules_blocks = [s.strip() for s in schedules.split("|")]

        for i, classroom in enumerate(classroom_list):
            # check if classroom is managed by the department
            if classroom.startswith("18"):
                continue
            # check if classroom already exists
            classroom_data = await get_classroom_by_location(location=classroom)
            if classroom_data is None:
                # create classroom
                new_classroom = ClassroomRequest(
                    capacity=(
                        None if classroom in ("INGENIA", "UDE@") else int(row["CUPO"])
                    ),
                    ownDepartment=True if classroom.startswith("18") else False,
                    location=classroom,
                    virtualMode=classroom in ("INGENIA", "UDE@"),
                )
                classroom_data = await add_classroom(classroom=new_classroom)

            # check if there are enough schedules for classrooms
            if i >= len(schedules_blocks):
                raise HTTPException(
                    status_code=400,
                    detail=f"Error: Not enough schedules for classroom {classroom}",
                )
            schedule_block = schedules_blocks[i]
            individual_schedule = schedule_block.split(" ")
            # Get the schedules for the each classroom
            for schedule in individual_schedule:
                print(f"Classroom: {classroom}, Schedule: {schedule}")
                # check if the object classroom_x_group already exists
                classroom_x_group = await get_group_classroom(
                    classroomId=classroom_data.id,
                    groupId=group_data.id,
                    schedule=schedule,
                )
                if classroom_x_group and classroom_x_group.schedule == schedule:
                    print(
                        f"Classroom x group {classroom} already exists for group {group_data.code} and schedule {schedule}"
                    )
                    continue

                # get days from schedule
                days = get_days_from_schedule(schedule=schedule)

                # Check that location of classroom is not in ('INGENIA', 'UDE@')
                if classroom not in ("INGENIA", "UDE@"):
                    # check if there is a conflict with the existing schedules
                    classrooms_groups = await get_classroom_and_schedules(
                        classroomId=classroom_data.id, days=days
                    )
                    if len(classrooms_groups) > 0:
                        # check if there is a conflict with the existing schedules
                        if has_conflict(
                            [cg.schedule for cg in classrooms_groups], schedule
                        ):
                            raise HTTPException(
                                status_code=400,
                                detail=f"Error: Conflict with existing schedules for classroom {classroom} and schedule {schedule}",
                            )

                # create classroom_x_group
                print(
                    f"Creating classroom x group for classroom {classroom} and group {group_data.code}"
                )
                await database.classroom_x_group.create(
                    data={
                        "classroomId": classroom_data.id,
                        "groupId": group_data.id,
                        "schedule": schedule,
                    }
                )
    # free memory
    del df
    gc.collect()


def get_days_from_schedule(schedule: str):
    i = 0
    days = []
    while i < len(schedule) and not schedule[i].isdigit():
        days.append(schedule[i])
        i += 1
    return days


def parse_schedule(schedule: str):
    # get the hour part of the schedule
    hours_part = "".join(filter(lambda c: c.isdigit() or c == "-", schedule))
    starts, ends = hours_part.split("-")
    return int(starts), int(ends)


def has_conflict(existing_schedules: list[str], new_schedule: str) -> bool:

    new_start, new_end = parse_schedule(new_schedule)

    for schedule in existing_schedules:
        exist_start, exist_end = parse_schedule(schedule)
        if exist_start < new_end and new_start < exist_end:
            return True
    return False
