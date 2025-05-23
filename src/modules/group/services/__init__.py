import json
from src.database import database



async def get_all_groups():
    return await database.group.find_many()

async def add_group(data):
    return await database.group.create(data=data)

async def update_group_by_id(groupId: int, data):
    return await database.group.update(
        where={"id": groupId},
        data=data
    )
    
async def delete_group_by_id(groupId:int):
    return await database.group.delete(
        where={"id": groupId}
    )

async def create_academic_schedule_pesnum(data):
    return await database.academic_schedule_pensum.create(data=data)

async def get_academic_schedule_pensum_by_pensum_id_and_academic_schedule_id(pensum_id: int, academic_schedule_id: int):
    return await database.academic_schedule_pensum.find_first(where={"pensumId": pensum_id, "academicScheduleId": academic_schedule_id})

async def create_classroom_x_group(data):
    return await database.classroom_x_group.create(data=data)
    
async def get_groups_by_academic_schedule_id(academic_schedule_id: int):
    academic_schedules = await database.academic_schedule_pensum.find_many(
        where={
            'academicScheduleId': academic_schedule_id
        },
        include={
            'group': {
                'include': {
                    'classroom_x_group': True,
                        # 'include': {
                        #     'classroom_x_group_mainClassroomIdToclassroom': True
                        # }
                    # }
                    'mirror_group': True,
                    'subject': {
                        'include': {
                            'pensum': {
                                'include': {
                                    'academic_program': True
                                }
                            }
                        }
                    }
                }
            }
        }
    )
    groups = []
    for academic_schedule in academic_schedules:
        groups.extend(academic_schedule.group)
    return groups


        