from src.modules.group_classroom.services import (
    get_all_group_classrooms,
    add_message_group_classroom,
    get_message_group_classroom,
)
from typing import List, Dict
from src.modules.group_classroom.models import GroupClassroomResponse
from src.modules.group_classroom.models import MessageGroupClassroomRequest


async def check_schedule_or_classroom_modified():
    group_classrooms: List[GroupClassroomResponse]= await get_all_group_classrooms()
    print("Checking for modified schedules...")
    #group by group_id
    group_map: Dict[int, List[GroupClassroomResponse]] = {}
    for group_classroom in group_classrooms:
        group_map.setdefault(group_classroom.groupId, []).append(group_classroom)
    
    # check if the schedules are modified
    for group_id, group_classroom_list in group_map.items():
        #get the mainSchedules set of the group_classroom
        main_schedules = {gc.mainSchedule for gc in group_classroom_list}
        main_classroom_ids = {gc.mainClassroomId for gc in group_classroom_list}

        #check if auxSchedule is in set of mainSchedules
        for gc in group_classroom_list:
            if gc.auxSchedule not in main_schedules:
                print(f"Group {group_id} has a modified schedule: {gc.auxSchedule}")
                #verify if message already exists
                message = await get_message_group_classroom(
                    group_id=group_id,
                    message_type=1,
                )
                if not message:
                    #create message
                    message = MessageGroupClassroomRequest(
                        groupId=group_id,
                        messageTypeId=1,
                        detail=f"Group {group_id} has a modified schedule: {gc.auxSchedule}",
                )
                    await add_message_group_classroom(message)
            #verify if auxClassroomId is in the set of mainClassroomId
            if gc.auxClassroomId not in main_classroom_ids:
                print(f"Group {group_id} has a modified classroom: {gc.auxClassroomId}")
                #verify if message already exists
                message = await get_message_group_classroom(
                    group_id=group_id,
                    message_type=2,
                )
                if not message:
                    #create message
                    message = MessageGroupClassroomRequest(
                        groupId=group_id,
                        messageTypeId=2,
                        detail=f"Group {group_id} has a modified classroom: {gc.auxClassroomId}",
                    )
                    await add_message_group_classroom(message)


