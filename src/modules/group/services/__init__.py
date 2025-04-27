from src.database import database
from src.modules.group.models import GroupRequest



async def get_all_groups():
    return await database.group.find_many()

async def add_group(data: GroupRequest):
    return await database.group.create(data = {
        "modality": data.modality,
        "groupSize": data.groupSize,
        "code": data.code,
        "subject": {
            "connect": {"id": data.subjectId}
        },
        "mirror_group": {
            "connect": {"id": data.mirrorGroupId}
        },
        "academic_schedule":{
            "connect": {"id": data.academicScheduleId}
        }
    })

async def update_group_by_id(groupId: int, data):
    return await database.group.update(
        where={"id": groupId},
        data=data
    )
    
async def delete_group_by_id(groupId:int):
    return await database.group.delete(
        where={"id": groupId}
    )

async def get_group_by_code_and_subject_code(code: int, subject_code: str):
    return await database.group.find_first(
        where={
            "code": code,
            "subject": { 
                "code": subject_code
            }
        }
    )


        