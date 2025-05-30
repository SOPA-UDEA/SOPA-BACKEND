from src.modules.group_classroom.services import (
    get_all_group_classrooms,
    add_message_group_classroom,
    get_message_group_classroom,
    delete_message_group_classroom,
)
from typing import List, Dict
from src.modules.group_classroom.models import GroupClassroomResponse
from src.modules.group_classroom.models import MessageGroupClassroomRequest


async def check_schedule_or_classroom_modified():
    CLASSROOM_MODIFIED_MESSAGE_TYPE = 2
    SCHEDULE_MODIFIED_MESSAGE_TYPE = 1
    CLASSROOMS_UNDEFINED = (
        "BUSCAR AULA",
        "BUSCAR AULA CON MEDIOS",
        "BUSCAR SALA DE CÓMPUTO",
    )
    group_classrooms: List[GroupClassroomResponse] = await get_all_group_classrooms()
    print("Checking for modified schedules...")
    # group by group_id
    group_map: Dict[int, List[GroupClassroomResponse]] = {}
    for group_classroom in group_classrooms:
        group_map.setdefault(group_classroom.groupId, []).append(group_classroom)

    # check if the schedules and classrooms are modified
    for group_id, group_classroom_list in group_map.items():
        # get the mainSchedules set of the group_classroom
        main_schedules = {gc.mainSchedule for gc in group_classroom_list}
        main_classroom_ids = {gc.mainClassroomId for gc in group_classroom_list}

        # check if auxSchedule is in set of mainSchedules
        for gc in group_classroom_list:
            # if the mainClassroomId is in the set of CLASSROOMS_UNDEFINED, skip it
            if gc.mainClassroom.location in CLASSROOMS_UNDEFINED:
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
                        detail=f"Group {group_id} has a modified schedule: {gc.auxSchedule}",
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
                print(f"Group {group_id} has a modified classroom: {gc.auxClassroomId}")

                if not classroomMessage:
                    # create message
                    message = MessageGroupClassroomRequest(
                        groupId=group_id,
                        messageTypeId=CLASSROOM_MODIFIED_MESSAGE_TYPE,
                        detail=f"Group {group_id} has a modified classroom: {gc.auxClassroomId}",
                    )
                    await add_message_group_classroom(message)
            else:
                # if the auxClassroomId is in the set of mainClassroomId and there is a message, delete it
                if classroomMessage:
                    await delete_message_group_classroom(
                        group_id=group_id,
                        message_type=CLASSROOM_MODIFIED_MESSAGE_TYPE,
                    )
