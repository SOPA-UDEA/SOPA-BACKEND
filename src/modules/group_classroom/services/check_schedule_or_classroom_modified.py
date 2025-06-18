from fastapi import HTTPException
from src.modules.group_classroom.services import (
    add_message_group_classroom,
    get_message_group_classroom,
    delete_message_group_classroom,
)
from typing import List, Dict
from src.modules.group_classroom.models import GroupClassroomResponse
from src.modules.group_classroom.models import MessageGroupClassroomRequest
from src.modules.group.models import GroupListResponse
from src.modules.group_classroom.helpers import (
    get_pensum_and_academic_schedule_pensum_id,
)
from src.modules.group.services import (
    get_all_groups_by_schedule_pensum_id,
)
from src.modules.academic_schedule.models import ScheduleRequestDrai


async def check_schedule_or_classroom_modified(schedule_request: ScheduleRequestDrai):
    CLASSROOM_MODIFIED_MESSAGE_TYPE = 2
    SCHEDULE_MODIFIED_MESSAGE_TYPE = 1

    semester = schedule_request.semester
    pensum_id = schedule_request.pensumId
    _, academic_schedule_pensum_id = await get_pensum_and_academic_schedule_pensum_id(
        semester, pensum_id
    )
    schedule_pensum_ids = [academic_schedule_pensum_id.id]
    res: GroupListResponse = await get_all_groups_by_schedule_pensum_id(
        schedule_pensum_ids
    )
    groups = res["data"]
    if not groups:
        raise HTTPException(
            status_code=404,
            detail=f"No groups found for academic schedule pensum ID {academic_schedule_pensum_id.id}",
        )
    group_classrooms: List[GroupClassroomResponse] = []
    for group in groups:
        print(f"classroom_x_group for group {group.id}")
        group_classrooms.extend(group.classroom_x_group)

    print("Checking for modified schedules...")
    # group by group_id
    group_map: Dict[int, List[GroupClassroomResponse]] = {}
    for group_classroom in group_classrooms:
        group_map.setdefault(group_classroom.groupId, []).append(group_classroom)

    # check if the schedules and classrooms are modified
    for group_id, group_classroom_list in group_map.items():
        # get the mainSchedules set of the group_classroom
        main_schedules = {
            gc.mainSchedule for gc in group_classroom_list if gc.mainSchedule
        }
        main_classroom_ids = {
            gc.mainClassroomId for gc in group_classroom_list if gc.mainClassroomId
        }

        # check if auxSchedule is in set of mainSchedules
        for gc in group_classroom_list:
            # if the mainClassroomId is a pointer, skip it
            if (
                not gc.auxSchedule
                or not gc.auxClassroomId
                or not gc.mainClassroom
                or not gc.mainSchedule
            ):
                print(f"Skipping group classroom {gc.id} due to missing data")
                continue
            if gc.mainClassroom.isPointer:
                print(f"Skipping classroom {gc.mainClassroomId}")
                continue

            print(f"validating modified schedule for group classroom {gc.id}")
            scheduleMessage = await get_message_group_classroom(
                group_id=group_id,
                message_type=SCHEDULE_MODIFIED_MESSAGE_TYPE,
            )
            if gc.auxSchedule not in main_schedules:
                print(f"Group {group_id} has a modified schedule: {gc.auxSchedule}")
                # verify if message already exists
                if not scheduleMessage:
                    # create message
                    message = MessageGroupClassroomRequest(
                        groupId=group_id,
                        messageTypeId=SCHEDULE_MODIFIED_MESSAGE_TYPE,
                        detail=f"El grupo {group_id} tiene un horario modificado: {gc.auxSchedule}",
                    )
                    await add_message_group_classroom(message)
            else:
                # if the auxSchedule is in the set of mainSchedules and there is a message, delete it
                if scheduleMessage:
                    await delete_message_group_classroom(
                        group_id=group_id,
                        message_type=SCHEDULE_MODIFIED_MESSAGE_TYPE,
                    )

            # verify if auxClassroomId is in the set of mainClassroomId
            # verify if message already exists for auxClassroomId
            classroomMessage = await get_message_group_classroom(
                group_id=group_id,
                message_type=CLASSROOM_MODIFIED_MESSAGE_TYPE,
            )
            if gc.auxClassroomId not in main_classroom_ids:
                print(
                    f"El grupo {group_id} tiene un aula modificada: {gc.auxClassroomId}"
                )

                if not classroomMessage:
                    # create message
                    message = MessageGroupClassroomRequest(
                        groupId=group_id,
                        messageTypeId=CLASSROOM_MODIFIED_MESSAGE_TYPE,
                        detail=f"El grupo {group_id} tiene un aula modificada: {gc.auxClassroom.location}",
                    )
                    await add_message_group_classroom(message)
            else:
                # if the auxClassroomId is in the set of mainClassroomId and there is a message, delete it
                if classroomMessage:
                    await delete_message_group_classroom(
                        group_id=group_id,
                        message_type=CLASSROOM_MODIFIED_MESSAGE_TYPE,
                    )
