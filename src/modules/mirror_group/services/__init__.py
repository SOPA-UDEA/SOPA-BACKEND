import json
from src.database import database



async def get_all_mirror_groups():
    return await database.mirror_group.find_many()

async def create_mirror_group(data):
    return await database.mirror_group.create(data=data)     