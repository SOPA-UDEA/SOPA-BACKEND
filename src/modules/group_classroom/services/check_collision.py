from fastapi import HTTPException
from typing import List
from src.modules.group_classroom.models import MessageGroupClassroomRequest
from src.modules.group_classroom.models import GroupClassroomResponse
from src.modules.group.services import get_groups_by_academic_schedule_id
from src.modules.academic_schedule.services import (
    get_schedule_by_semester,
)
from src.modules.group_classroom.services import (
    get_classrooms_and_schedules,
    add_message_group_classroom,
    get_message_group_classroom,
    delete_message_group_classroom,
)
from src.modules.group.services import (
    get_all_groups_by_mirror_group_id,
    get_group_by_id,
)


async def check_collision(semester: str):
    COLLISION_MESSAGE_TYPE = 7
    academic_schedule = await get_schedule_by_semester(semester)
    if not academic_schedule:
        raise HTTPException(
            status_code=404,
            detail=f"No academic schedule found for semester {semester}",
        )

    # get groups by academic schedule
    groups = await get_groups_by_academic_schedule_id(
        academic_schedule.id
    )
    if not groups:
        raise HTTPException(
            status_code=404,
            detail=f"No groups found for academic schedule {academic_schedule.academicScheduleId}",
        )

    group_classrooms: List[GroupClassroomResponse] = []
    for group in groups:
        group_classrooms.extend(group.classroom_x_group)

    for current_gc in group_classrooms:
        main_classroom = current_gc.mainClassroom
        main_schedule = current_gc.mainSchedule
        group_id = current_gc.groupId

        print(f"validating collision for group main_classroom {current_gc.id}")
        # If the main_classroom is virtual or has a specific location in (18325, 18210), skip it
        if (
            main_classroom.virtualMode
            or main_classroom.hasRoom
            or main_classroom.isPointer
        ):
            print(f"Skipping main_classroom {main_classroom.location}")
            continue

        group = await get_group_by_id(group_id)

        mirror_group_ids = set()
        if group.mirrorGroupId:
            mirror_groups = await get_all_groups_by_mirror_group_id(group.mirrorGroupId)
            mirror_group_ids = {g.id for g in mirror_groups}
        print(f"mirror group ids: {mirror_group_ids}")
        # Get the main schedule of the group
        days = get_days_from_schedule(main_schedule)
        print(f"days: {days}")
        # search for the main_classrooms and schedules of the main main_classroom
        main_classrooms_and_schedules = await get_classrooms_and_schedules(
            main_classroom.id, days
        )
        for other_gc in main_classrooms_and_schedules:
            # Avoid checking mirror groups and the same group
            if (
                other_gc.groupId == group_id
                or other_gc.group.mirrorGroupId in mirror_group_ids
            ):
                print(
                    f"Skipping group {other_gc.groupId} as it is a mirror group or the same group"
                )
                continue

            collision = await get_message_group_classroom(
                group_id=current_gc.groupId, message_type=COLLISION_MESSAGE_TYPE
            )
            # Check if the schedules have a conflict
            if has_conflict(main_schedule, other_gc.mainSchedule):

                if not collision:
                    print(
                        f"Adding collision message for group main_classroom {current_gc.id}"
                    )
                    message = MessageGroupClassroomRequest(
                        groupId=current_gc.groupId,
                        messageTypeId=COLLISION_MESSAGE_TYPE,
                        detail=f"Conflicto con el grupo {other_gc.group.id} ({other_gc.mainClassroom.location}) - Horario: {other_gc.mainSchedule}",
                    )
                    await add_message_group_classroom(message)
            else:
                # If the schedules do not have a conflict, remove the message
                if collision:
                    print(
                        f"Removing collision message for group main_classroom {current_gc.id}"
                    )
                    await delete_message_group_classroom(
                        group_id=current_gc.groupId, message_type=COLLISION_MESSAGE_TYPE
                    )


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


def has_conflict(schedule1: str, schedule2: str) -> bool:
    # get the days from the schedule
    days1 = get_days_from_schedule(schedule1)
    days2 = get_days_from_schedule(schedule2)
    # check if the schedules have the same day
    if not any(day in days1 for day in days2):
        return False
    # get the hours from the schedule
    start1, end1 = parse_schedule(schedule1)
    start2, end2 = parse_schedule(schedule2)
    # check if the schedules have a conflict
    return start1 < end2 and start2 < end1
