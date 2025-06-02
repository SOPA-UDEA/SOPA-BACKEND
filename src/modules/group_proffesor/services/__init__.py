from typing import List
from src.database import database

async def update_group_proffesor(data: List[int], groupId: int):

    await database.group_x_professor.delete_many(
        where={"groupId": groupId}
    )

    for professor_id in data:
        await database.group_x_professor.create(
            data={
                "groupId": groupId,
                "professorId": professor_id
            }
        )


