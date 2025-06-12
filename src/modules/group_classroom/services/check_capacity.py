from typing import List
from fastapi import HTTPException
from src.modules.group_classroom.services import (
    add_message_group_classroom,
    get_message_group_classroom,
    delete_message_group_classroom,
)
from src.modules.group_classroom.helpers import (
    get_pensum_and_academic_schedule_pensum_id,
)
from src.modules.group.services import (
    get_all_groups_by_schedule_pensum_id,
    get_group_by_id,
)
from src.modules.academic_schedule.models import ScheduleRequestDrai
from src.modules.group_classroom.models import MessageGroupClassroomRequest
from src.modules.group_classroom.models import GroupClassroomResponse


async def check_capacity(schedule_request: ScheduleRequestDrai):
    """
    Check the capacity of all group classrooms and add messages if any exceed the limit.
    This function iterates through all group classrooms, checks if the number of students exceeds the classroom capacity,
    and adds a message if it does. It also deletes any existing messages of type 4 (capacity exceeded).
    """
    print("Checking capacity for group classrooms...")

    semester = schedule_request.semester
    pensum_id = schedule_request.pensumId

    _, academic_schedule_pensum_id = await get_pensum_and_academic_schedule_pensum_id(
        semester, pensum_id
    )
    schedule_pensum_ids = [academic_schedule_pensum_id.id]

    groups = await get_all_groups_by_schedule_pensum_id(schedule_pensum_ids)
    if not groups:
        raise HTTPException(
            status_code=404,
            detail=f"No groups found for academic schedule pensum ID {academic_schedule_pensum_id.id}",
        )
    group_classrooms: List[GroupClassroomResponse] = []

    for group in groups:
        group_classrooms.extend(group.classroom_x_group)

    CAPACITY_EXCEEDED_MESSAGE_TYPE = 4  # Assuming 4 is the type for capacity exceeded

    for current_gc in group_classrooms:
        main_classroom = current_gc.mainClassroom
        group = await get_group_by_id(current_gc.groupId)
        if main_classroom.isPointer or main_classroom.virtualMode:
            print(
                f"Skipping group classroom {current_gc.id} due to undefined classroom or virtual mode"
            )
            continue
        print(f"Checking capacity for group classroom {current_gc.id}")
        # Check if a message already exists for this group and type 4
        existing_message = await get_message_group_classroom(
            group_id=current_gc.groupId, message_type=CAPACITY_EXCEEDED_MESSAGE_TYPE
        )
        if main_classroom.capacity < group.maxSize:
            print(f"Group {group.id} exceeds capacity of classroom {main_classroom.id}")

            if not existing_message:
                # Add a new message indicating capacity exceeded
                message_data = MessageGroupClassroomRequest(
                    groupId=current_gc.groupId,
                    messageTypeId=CAPACITY_EXCEEDED_MESSAGE_TYPE,
                    detail=f"El grupo {group.id} supera la capacidad del aula {main_classroom.id} ({group.maxSize}/{main_classroom.capacity} estudiantes)",
                )
                await add_message_group_classroom(message_data)
                print(f"Added message for group {group.id} exceeding capacity")
        else:
            # If the group is within capacity, delete any existing message of type 4
            if existing_message:
                await delete_message_group_classroom(
                    group_id=current_gc.groupId,
                    message_type=CAPACITY_EXCEEDED_MESSAGE_TYPE,
                )
                print(f"Deleted message for group {group.id} exceeding capacity")
