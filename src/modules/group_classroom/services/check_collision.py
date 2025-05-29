from src.modules.group_classroom.models import MessageGroupClassroomRequest
from src.modules.group_classroom.services import (
    get_classrooms_and_schedules,
    get_all_group_classrooms,
    add_message_group_classroom,
    get_message_group_classroom,
    delete_message_group_classroom,
)
from src.modules.group.services import (
    get_all_groups_by_mirror_group_id,
    get_group_by_id,
)
from src.modules.classroom.services import get_classroom_by_id


async def check_collision():
    VIRTUAL_CLASSROOMS = ("INGENIA", "UDE@")
    CLASSROOM_WITH_ROOM = ("18325", "18210")
    CLASSROOM_UNDEFINED = (
        "BUSCAR AULA",
        "BUSCAR AULA CON MEDIOS",
        "BUSCAR SALA DE CÓMPUTO",
    )
    COLLISION_MESSAGE_TYPE = 7
    group_classrooms = await get_all_group_classrooms()
    print("Checking for collisions...")
    for current_gc in group_classrooms:
        main_classroom_id = current_gc.mainClassroomId
        main_schedule = current_gc.mainSchedule
        group_id = current_gc.groupId

        print(f"validating collision for group classroom {current_gc.id}")
        classroom = await get_classroom_by_id(main_classroom_id)
        if classroom:
            # If the classroom is virtual or has a specific location in (18325, 18210), skip it
            if (
                classroom.location in VIRTUAL_CLASSROOMS
                or classroom.location in CLASSROOM_WITH_ROOM
                or classroom.location in CLASSROOM_UNDEFINED
            ):
                print(f"Skipping classroom {classroom.location}")
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
        # search for the classrooms and schedules of the main classroom
        classrooms_and_schedules = await get_classrooms_and_schedules(
            main_classroom_id, days
        )
        for other_gc in classrooms_and_schedules:
            # Avoid checking mirror groups and the same group
            if other_gc.groupId == group_id or other_gc.groupId in mirror_group_ids:
                continue

            collision = await get_message_group_classroom(
                group_id=current_gc.groupId, message_type=COLLISION_MESSAGE_TYPE
            )
            # Check if the schedules have a conflict
            if has_conflict(main_schedule, other_gc.mainSchedule):

                if not collision:
                    print(
                        f"Adding collision message for group classroom {current_gc.id}"
                    )
                    message = MessageGroupClassroomRequest(
                        groupId=current_gc.groupId,
                        messageTypeId=COLLISION_MESSAGE_TYPE,
                        detail=f"Collision with group {other_gc.groupId} and schedule {other_gc.mainSchedule}",
                    )
                    await add_message_group_classroom(message)
            else:
                # If the schedules do not have a conflict, remove the message
                if collision:
                    print(
                        f"Removing collision message for group classroom {current_gc.id}"
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
