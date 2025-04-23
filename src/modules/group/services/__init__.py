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

        