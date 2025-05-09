from src.modules.group_classroom.models import MessageGroupClassroomRequest
from src.modules.group_classroom.services import (
    get_classrooms_and_schedules,
    get_all_group_classrooms,
    add_message_group_classroom,
    get_message_group_classroom,
)
from src.modules.group.services import get_all_groups_by_mirror_group_id, get_group_by_id

async def check_collision():
    group_classrooms = await get_all_group_classrooms()
    print("Checking for collisions...")
    for current_gc in group_classrooms:
        main_classroom_id = current_gc.mainClassroomId
        main_schedule = current_gc.mainSchedule
        group_id = current_gc.groupId

        group = await get_group_by_id(group_id)

        mirror_group_ids = set()
        if group.mirrorGroupId:
            mirror_groups = await get_all_groups_by_mirror_group_id(group.mirrorGroupId)
            mirror_group_ids = {g.id for g in mirror_groups}

        # Get the main schedule of the group
        days = get_days_from_schedule(main_schedule)

        # search for the classrooms and schedules of the main classroom
        classrooms_and_schedules = await get_classrooms_and_schedules(
            main_classroom_id, days
        )
        for other_gc in classrooms_and_schedules:
            # Avoid checking mirror groups and the same group
            if other_gc.groupId == group_id or other_gc.groupId in mirror_group_ids:
                continue
            # Check if the schedules have a conflict
            if has_conflict(main_schedule, other_gc.mainSchedule):
                collision = await get_message_group_classroom(
                    classroom_group_id=current_gc.id,
                    message_type=5,
                )
                if not collision:
                    message = MessageGroupClassroomRequest(
                        classroomGroupId=current_gc.id, messageTypeId=5
                    )
                    await add_message_group_classroom(message)


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
