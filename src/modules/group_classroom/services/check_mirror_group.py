from typing import Dict, List, Set
from src.modules.group_classroom.services import (
    add_message_group_classroom,
    get_message_group_classroom,
    delete_message_group_classroom,
    get_all_group_classrooms,
)
from src.modules.mirror_group.services import get_mirror_group_by_id
from src.modules.group_classroom.models import (
    MessageGroupClassroomRequest,
    GroupClassroomResponse,
)


async def check_mirror_group():
    """
    Check mirror groups for consistency in schedules and classrooms.
    This function retrieves all group classrooms, groups them by their mirror group ID,
    and checks if the schedules and classrooms of each group within a mirror group are consistent.
    If inconsistencies are found, it adds messages to the respective groups.
    """
    group_classrooms = await get_all_group_classrooms()

    # Group by mirror group ID
    mirror_group_map: Dict[int, Dict[int, List[GroupClassroomResponse]]] = {}

    for gc in group_classrooms:
        mirror_id = gc.group.mirrorGroupId
        if not mirror_id:
            continue
        mirror_group_map.setdefault(mirror_id, {}).setdefault(gc.groupId, []).append(gc)

    MIRROR_GROUP_SHEDULE_MESSAGE_TYPE = 5
    MIRROR_GROUP_CLASSROOM_MESSAGE_TYPE = 6

    for mirror_id, group_dict in mirror_group_map.items():
        print(f"Checking mirror group {mirror_id}")
        # if the mirror group has only one group, skip it
        if len(group_dict) <= 1:
            print(f"Mirror group {mirror_id} has only one group, skipping.")
            continue
        # Create sets for schedules and classrooms for each group in the mirror group
        # This will hold the schedules and classrooms for each group in the mirror group
        schedule_sets: Dict[int, Set[str]] = {
            gid: {gc.mainSchedule for gc in gcs} for gid, gcs in group_dict.items()
        }
        classroom_sets: Dict[int, Set[int]] = {
            gid: {gc.mainClassroomId for gc in gcs} for gid, gcs in group_dict.items()
        }

        # Use the first group as the reference for comparison
        reference_gid = next(iter(group_dict))
        reference_schedules = schedule_sets[reference_gid]
        reference_classrooms = classroom_sets[reference_gid]

        for gid in group_dict:
            # Get the schedules and classrooms for the current group
            print(f"Checking group {gid} in mirror group {mirror_id}")
            schedules = schedule_sets[gid]
            classrooms = classroom_sets[gid]

            mirror_group_search = await get_mirror_group_by_id(mirror_id)
            if not mirror_group_search:
                print(f"Mirror group {mirror_id} not found, skipping group {gid}.")
                continue

            # Compare sets of schedules
            if schedules != reference_schedules:
                print(
                    f"Group {gid} has different schedules than the reference group {reference_gid}"
                )
                existing = await get_message_group_classroom(
                    group_id=gid,
                    message_type=MIRROR_GROUP_SHEDULE_MESSAGE_TYPE,
                )
                if not existing:
                    await add_message_group_classroom(
                        MessageGroupClassroomRequest(
                            groupId=gid,
                            messageTypeId=MIRROR_GROUP_SHEDULE_MESSAGE_TYPE,
                            detail=f"Schedules different between mirror groups in set {mirror_group_search.name}.",
                        )
                    )
            else:
                existing = await get_message_group_classroom(
                    group_id=gid,
                    message_type=MIRROR_GROUP_SHEDULE_MESSAGE_TYPE,
                )
                if existing:
                    await delete_message_group_classroom(
                        group_id=gid,
                        message_type=MIRROR_GROUP_SHEDULE_MESSAGE_TYPE,
                    )

            # Comparar sets de aulas
            if classrooms != reference_classrooms:
                print(
                    f"Group {gid} has different classrooms than the reference group {reference_gid}"
                )
                existing = await get_message_group_classroom(
                    group_id=gid,
                    message_type=MIRROR_GROUP_CLASSROOM_MESSAGE_TYPE,
                )
                if not existing:
                    await add_message_group_classroom(
                        MessageGroupClassroomRequest(
                            groupId=gid,
                            messageTypeId=MIRROR_GROUP_CLASSROOM_MESSAGE_TYPE,
                            detail=f"Classrooms different between mirror groups in set {mirror_group_search.name}.",
                        )
                    )
            else:
                existing = await get_message_group_classroom(
                    group_id=gid,
                    message_type=MIRROR_GROUP_CLASSROOM_MESSAGE_TYPE,
                )
                if existing:
                    await delete_message_group_classroom(
                        group_id=gid,
                        message_type=MIRROR_GROUP_CLASSROOM_MESSAGE_TYPE,
                    )
