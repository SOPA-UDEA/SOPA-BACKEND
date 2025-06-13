import pandas as pd
from collections import defaultdict
from fastapi import HTTPException
from fastapi.responses import StreamingResponse
from io import BytesIO
from src.modules.academic_schedule.models import (
    ScheduleRequestDrai,
)
from src.modules.group.services import (
    get_all_groups_by_schedule_pensum_id,
)
from src.modules.group_classroom.helpers import (
    get_pensum_and_academic_schedule_pensum_id,
)


async def export_group_classrooms_to_excel(
    scheduleRequest: ScheduleRequestDrai,
) -> StreamingResponse:
    """
    Export group classrooms to an Excel file.
    """
    # Fetch group classrooms from the database
    pensum, academic_schedule_pensum_id = (
        await get_pensum_and_academic_schedule_pensum_id(
            scheduleRequest.semester, scheduleRequest.pensumId
        )
    )
    schedule_pensum_ids = [academic_schedule_pensum_id.id]

    groups = await get_all_groups_by_schedule_pensum_id(schedule_pensum_ids)
    if not groups:
        raise HTTPException(
            status_code=404,
            detail=f"No groups found for semester {scheduleRequest.semester} and pensum ID {scheduleRequest.pensumId}.",
        )

    facs = [group.subject.code[:2] for group in groups]
    deps = [group.subject.code[2:4] for group in groups]
    ides = [
        "ISI" if pensum.academic_program.modalityAcademic == "Presencial" else "IDS"
        for _ in groups
    ]
    mats = [group.subject.code[4:] for group in groups]
    grs = [group.code for group in groups]
    subjects_names = [group.subject.name for group in groups]
    capacities = [group.groupSize for group in groups]
    matrs = [group.registeredPlaces for group in groups]

    classrooms = []
    schedules = []
    Indentifications = []
    professors = []

    for group in groups:
        # Extract the identifications and professors for each group
        identifications_aux = []
        professors_aux = []

        for group_professor in group.group_x_professor:
            identifications_aux.append(group_professor.professor.identification)
            professors_aux.append(group_professor.professor.name)

        Indentifications.append(
            "|".join(identifications_aux) if identifications_aux else None
        )
        professors.append("|".join(professors_aux) if professors_aux else None)

        # Extract the classrooms and schedules for each group
        classrooms_aux = []
        schedules_aux = []

        grouped = defaultdict(list)
        for classroom in group.classroom_x_group:
            grouped[classroom.mainClassroom.location].append(classroom.mainSchedule)

        for classroom, schedules_list in grouped.items():
            classrooms_aux.append(classroom)
            schedules_aux.append(" ".join(schedules_list))

        classrooms.append("|".join(classrooms_aux))
        schedules.append("|".join(schedules_aux))

    # Create a DataFrame with the extracted data
    data = {
        "FAC": facs,
        "DEP": deps,
        "IDE": ides,
        "MAT": mats,
        "GR": grs,
        "NOMBRE MATERIA": subjects_names,
        "CUPO": capacities,
        "MATR": matrs,
        "AULA": classrooms,
        "HORARIO": schedules,
        "IDENTIFICACION": Indentifications,
        "PROFESOR(ES)": professors,
    }
    df = pd.DataFrame(data)
    df = df.sort_values(by=["FAC", "DEP", "MAT", "GR"])
    df = df.astype(str).applymap(lambda x: x.encode("utf-8", "ignore").decode("utf-8"))
    df.replace("", None, inplace=True)

    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(
            writer,
            index=False,
            sheet_name="programacion_academica",
        )
    output.seek(0)

    headers = {
        "Content-Disposition": f"attachment; filename={pensum.academic_program.name}_version_{pensum.version}_semester_{scheduleRequest.semester}.xlsx",
        "Content-Type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    }
    return StreamingResponse(
        output,
        headers=headers,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
