from src.modules.group_classroom.services import (
    add_message_group_classroom,
    get_message_group_classroom,
    delete_message_group_classroom,
    get_all_group_classrooms,
)
from src.modules.group_classroom.models import MessageGroupClassroomRequest


async def check_capacity():
    """
    Check the capacity of all group classrooms and add messages if any exceed the limit.
    This function iterates through all group classrooms, checks if the number of students exceeds the classroom capacity,
    and adds a message if it does. It also deletes any existing messages of type 4 (capacity exceeded).
    """
    group_classrooms = await get_all_group_classrooms()
    print("Checking capacity for group classrooms...")

    CAPACITY_EXCEEDED_MESSAGE_TYPE = 4  # Assuming 4 is the type for capacity exceeded
    CLASSROOM_UNDEFINED = (
        "BUSCAR AULA",
        "BUSCAR AULA CON MEDIOS",
        "BUSCAR SALA DE CÓMPUTO",
    )

    for current_gc in group_classrooms:
        main_classroom = current_gc.mainClassroom
        group = current_gc.group
        if main_classroom.location in CLASSROOM_UNDEFINED or main_classroom.virtualMode:
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
                    detail=f"Group {group.id} exceeds the capacity of classroom {main_classroom.location}.",
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
