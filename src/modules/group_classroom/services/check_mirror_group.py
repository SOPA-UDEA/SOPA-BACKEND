from fastapi import HTTPException
from typing import Dict, List, Set
from src.modules.group_classroom.services import (
    add_message_group_classroom,
    get_message_group_classroom,
    delete_message_group_classroom,
)
from src.modules.mirror_group.services import get_mirror_group_by_id
from src.modules.group_classroom.models import (
    MessageGroupClassroomRequest,
    GroupClassroomResponse,
)
from src.modules.group_classroom.helpers import (
    get_pensum_and_academic_schedule_pensum_id,
)
from src.modules.group.services import (
    get_all_groups_by_schedule_pensum_id,
    get_group_by_id,
)
from src.modules.academic_schedule.models import ScheduleRequestDrai


async def check_mirror_group(schedule_request: ScheduleRequestDrai):
    """
    Check mirror groups for consistency in schedules and classrooms.
    This function retrieves all group classrooms, groups them by their mirror group ID,
    and checks if the schedules and classrooms of each group within a mirror group are consistent.
    If inconsistencies are found, it adds messages to the respective groups.
    """
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
    # Retrieve all group classrooms
    group_classrooms: List[GroupClassroomResponse] = []
    for group in groups:
        group_classrooms.extend(group.classroom_x_group)
    # Group by mirror group ID
    mirror_group_map: Dict[int, Dict[int, List[GroupClassroomResponse]]] = {}

    for gc in group_classrooms:
        group = await get_group_by_id(gc.groupId)
        mirror_id = group.mirrorGroupId
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

        aux_schedule_sets: Dict[int, Set[str]] = {
            gid: {gc.auxSchedule for gc in gcs if gc.auxSchedule} for gid, gcs in group_dict.items()
        }

        aux_classroom_sets: Dict[int, Set[int]] = {
            gid: {gc.auxClassroomId for gc in gcs if gc.auxClassroomId} for gid, gcs in group_dict.items()
        }

        # Use the first group as the reference for comparison
        reference_gid = next(iter(group_dict))
        reference_schedules = schedule_sets[reference_gid]
        reference_classrooms = classroom_sets[reference_gid]
        reference_aux_schedules = aux_schedule_sets[reference_gid]
        reference_aux_classrooms = aux_classroom_sets[reference_gid]

        for gid in group_dict:
            # Get the schedules and classrooms for the current group
            print(f"Checking group {gid} in mirror group {mirror_id}")
            schedules = schedule_sets[gid]
            classrooms = classroom_sets[gid]
            aux_schedules = aux_schedule_sets[gid]
            aux_classrooms = aux_classroom_sets[gid]

            mirror_group_search = await get_mirror_group_by_id(mirror_id)
            if not mirror_group_search:
                print(f"Mirror group {mirror_id} not found, skipping group {gid}.")
                continue

            # Compare sets of schedules
            if schedules != reference_schedules or aux_schedules != reference_aux_schedules:
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
                            detail=f"Hay diferencias en los horarios entre los grupos espejo en el conjunto {mirror_group_search.name}.",
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
            if classrooms != reference_classrooms or aux_classrooms != reference_aux_classrooms:
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
                            detail=f"Hay diferencias en las aulas entre los grupos espejo en el conjunto {mirror_group_search.name}.",
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
