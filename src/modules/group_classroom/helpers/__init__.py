from fastapi import HTTPException
from typing import List
from src.modules.academic_schedule.services import (
    get_schedule_by_semester,
    add_schedule,
    get_academic_schedule_pensum_id,
    add_academic_schedule_pensum_id,
)
from src.modules.group_proffesor.services import (
    get_professor_by_identification,
    create_professor,
    get_group_professor_by_professor_id_and_group_id,
    create_group_professor,
)
from src.modules.pensum.services import get_pensum_by_id
from src.modules.academic_schedule.models import (
    AcademicSchedulePensumIdRequest,
    AcademicSchedulePensumIdResponse,
)
from src.modules.pensum.models import PensumResponse
from src.modules.group_proffesor.models import GroupProfessorRequest, ProfessorRequest


async def get_or_create_pensum_and_academic_schedule_pensum_id(
    semester: str, pensum_id: int
):
    # get the pensum from the database
    pensum = await get_pensum_by_id(pensum_id)
    if not pensum:
        raise HTTPException(
            status_code=400,
            detail=f"Pensum with ID {pensum_id} not found in the database",
        )

    # Get the academic schedule by semester
    academic_schedule = await get_schedule_by_semester(semester)
    if not academic_schedule:
        # create a new academic schedule if it does not exist
        scheduleCreate = {"semester": semester}
        academic_schedule = await add_schedule(scheduleCreate)

    # Get the academic schedule pensum ID
    academic_schedule_pensum_id_request = AcademicSchedulePensumIdRequest(
        academicScheduleId=academic_schedule.id,
        pensumId=pensum_id,
    )
    academic_schedule_pensum_id = await get_academic_schedule_pensum_id(
        academic_schedule_pensum_id_request
    )
    if not academic_schedule_pensum_id:
        # Create a new academic schedule pensum ID if it does not exist
        academic_schedule_pensum_id = await add_academic_schedule_pensum_id(
            academic_schedule_pensum_id_request
        )
    return pensum, academic_schedule_pensum_id


from typing import Tuple

async def get_pensum_and_academic_schedule_pensum_id(semester: str, pensum_id: int) -> Tuple[PensumResponse, AcademicSchedulePensumIdResponse]:
    # get the pensum from the database
    pensum = await get_pensum_by_id(pensum_id)
    if not pensum:
        raise HTTPException(
            status_code=400,
            detail=f"Pensum with ID {pensum_id} not found in the database",
        )

    # Get the academic schedule by semester
    academic_schedule = await get_schedule_by_semester(semester)
    if not academic_schedule:
        raise HTTPException(
            status_code=400,
            detail=f"Academic schedule for semester {semester} not found in the database",
        )

    # Get the academic schedule pensum ID
    academic_schedule_pensum_id_request = AcademicSchedulePensumIdRequest(
        academicScheduleId=academic_schedule.id,
        pensumId=pensum_id,
    )
    academic_schedule_pensum_id = await get_academic_schedule_pensum_id(
        academic_schedule_pensum_id_request
    )
    if not academic_schedule_pensum_id:
        raise HTTPException(
            status_code=400,
            detail=f"Academic schedule pensum ID for semester {semester} and pensum ID {pensum_id} not found in the database",
        )

    return pensum, academic_schedule_pensum_id


async def create_professors_for_group(
    professors: List, identification: List, group_id: int
):
    for i, professor in enumerate(professors):
        # Get the professor by identification
        prof = await get_professor_by_identification(identification[i])
        if not prof:
            # Create a new professor if it does not exist
            professor_request = ProfessorRequest(
                identification=identification[i], name=professor
            )
            prof = await create_professor(professor_request)

        # Get the group professor by professor ID and group ID
        groupProfessorRequest = GroupProfessorRequest(
            professorId=prof.id, groupId=group_id
        )
        group_professor = await get_group_professor_by_professor_id_and_group_id(
            groupProfessorRequest
        )
        if not group_professor:
            # Create a new group professor if it does not exist
            await create_group_professor(groupProfessorRequest)
