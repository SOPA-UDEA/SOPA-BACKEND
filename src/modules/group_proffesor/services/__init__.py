from typing import List
from src.database import database
from src.modules.group_proffesor.models import GroupProfessorRequest, ProfessorRequest


async def update_group_proffesor(data: List[int], groupId: int):

    await database.group_x_professor.delete_many(where={"groupId": groupId})

    for professor_id in data:
        await database.group_x_professor.create(
            data={"groupId": groupId, "professorId": professor_id}
        )


async def get_group_professor_by_professor_id_and_group_id(
    groupProfessorRequest: GroupProfessorRequest,
):
    return await database.group_x_professor.find_first(
        where={
            "professorId": groupProfessorRequest.professorId,
            "groupId": groupProfessorRequest.groupId,
        }
    )


async def create_group_professor(
    groupProfessorRequest: GroupProfessorRequest,
):
    return await database.group_x_professor.create(
        data={
            "professorId": groupProfessorRequest.professorId,
            "groupId": groupProfessorRequest.groupId,
        }
    )


async def get_professor_by_identification(identification: str):
    return await database.professor.find_first(where={"identification": identification})


async def create_professor(
    professorRequest: ProfessorRequest,
):
    return await database.professor.create(
        data={
            "identification": professorRequest.identification,
            "name": professorRequest.name,
        }
    )
