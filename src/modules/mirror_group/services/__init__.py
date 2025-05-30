from src.database import database



async def get_all_mirror_groups():
    return await database.mirror_group.find_many()

async def create_mirror_group(data):
    return await database.mirror_group.create(data=data)

async def get_mirror_group_by_id(mirror_group_id: int):
    return await database.mirror_group.find_unique(where={"id": mirror_group_id})     