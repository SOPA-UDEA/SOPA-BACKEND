from typing import List
from src.modules.group.models import GroupResponse
from src.modules.group_proffesor.services import update_group_proffesor
from src.database import database
from src.modules.group.models import GroupRequest, GroupUpdateRequest, GroupListResponse
import math
from collections import defaultdict
from typing import List, Dict, Tuple, Any

async def get_group_by_id(groupId: int) -> GroupResponse:
    return await database.group.find_first(where={"id": groupId})

def extract_schedules(schedule_str: str) -> List[str]:
    # Puedes hacer esto más robusto según el formato exacto de los horarios
    return [s.strip() for s in schedule_str.split(",") if s]

async def get_group_by_code_and_subject_code_and_academicSchedulePensumId(
    code: int, subject_code: str, academicSchedulePensumId: int
):
    return await database.group.find_first(
        where={
            "code": code,
            "subject": {"code": subject_code},
            "academicSchedulePensumId": academicSchedulePensumId,
        }
    )


async def add_group(data: GroupRequest):
    return await database.group.create(data=data.model_dump())


async def add_group_base(data: GroupRequest):
    return await database.group.create(data=data)


async def update_group_by_id(groupId: int, data: GroupUpdateRequest):
    await database.group.update(
        where={"id": groupId},
        data={
            "groupSize": data.groupSize,
            "modality": data.modality,
            "maxSize": data.maxSize,
            "registeredPlaces": data.registeredPlaces,
        },
    )

    await update_group_proffesor(data.professors, groupId)


async def delete_group_by_id(groupId: int):
    return await database.group.delete(where={"id": groupId})


async def subtract_group_number_for_greater_groups(groups, base: int):
    for group in groups:
        if base < group.code:
            await database.group.update(
                where={"id": group.id}, data={"code": group.code - 1}
            )


async def create_classroom_x_group(data):
    return await database.classroom_x_group.create(data=data)


async def get_groups_by_academic_schedule_id(
    academic_schedule_id: int,
) -> List[GroupResponse]:
    academic_schedules = await database.academic_schedule_pensum.find_many(
        where={"academicScheduleId": academic_schedule_id},
        include={
            "group": {
                "include": {
                    "classroom_x_group": {
                        "include": {
                            "mainClassroom": True,
                            "auxClassroom": True,
                        }
                    },
                    "group_x_professor": {"include": {"professor": True}},
                    "mirror_group": True,
                    "subject": {
                        "include": {"pensum": {"include": {"academic_program": True}}}
                    },
                }
            }
        },
    )
    groups = []
    for academic_schedule in academic_schedules:
        groups.extend(academic_schedule.group)
    return groups


async def get_all_groups_by_mirror_group_id(mirror_group_id: int):
    return await database.group.find_many(where={"mirrorGroupId": mirror_group_id})


async def get_group_by_id(groupId: int):
    return await database.group.find_first(where={"id": groupId})


async def get_groups_by_subjectId_and_academicSchedulePenusmId(
    subjectId: int, academicSchedulePensumId: int
):
    return await database.group.find_many(
        where={
            "subjectId": subjectId,
            "academicSchedulePensumId": academicSchedulePensumId,
        }
    )


async def soft_delete_group(groupId: int):
    return await database.group.update(
        where={"id": groupId},
        data={"code": 0, "groupSize": 0, "maxSize": 0, "registeredPlaces": 0},
    )


async def get_all_groups_by_schedule_pensum_id(
    schedule_pensum_ids: list[int], skip: int = 0, take: int = 15
) -> GroupListResponse:
    total = await database.group.count(
        where={"academicSchedulePensumId": {"in": schedule_pensum_ids}}
    )
    items = await database.group.find_many(
        where={"academicSchedulePensumId": {"in": schedule_pensum_ids}},
        skip=skip,
        take=take,
        include={
            "classroom_x_group": {
                "include": {
                    "mainClassroom": True,
                    "auxClassroom": True,
                }
            },
            "group_x_professor": {"include": {"professor": True}},
            "mirror_group": True,
            "subject": {"include": {"pensum": {"include": {"academic_program": True}}}},
        },
        order=[
            {"subject": {"level": "asc"}},
            {"subject": {"name": "asc"}},
            {"code": "asc"},
        ],
    )
    return {
        "total": total,
        "skip": skip,
        "take": take,
        "data": items,
    }


async def exist_base_groups(schedule_pensum_id: int):
    return await database.group.find_first(
        where={"academicSchedulePensumId": schedule_pensum_id}
    )

async def update_base_group(group):
    return await database.group.update(
        where={"id": group.id}, data={"code": group.code + 1}
    )


async def get_group_to_update(group_id):
    return await database.group.find_unique(
        where={"id": group_id},
        include={
            "classroom_x_group": {
                "include": {"mainClassroom": True},
                "orderBy": {"mainClassroom": {"id": "asc"}},
            },
            "group_x_professor": {
                "include": {"professor": True},
                "orderBy": {"professor": {"id": "asc"}},
            },
            "mirror_group": True,
            "subject": {"include": {"pensum": {"include": {"academic_program": True}}}},
        },
    )


async def update_mirror_group(group_ids: list[int]):
    if len(group_ids) < 2:
        return "At least two groups are required to validate mirror groups"

    groups = []

    for group_id in group_ids:
        group = await get_group_to_update(group_id)
        groups.append(group)

    reference_group = groups[0]

    for group in groups[1:]:
        # Validar pensum
        if group.academicSchedulePensumId == reference_group.academicSchedulePensumId:
            return "groups are not mirrors"

        # Validar cantidad de aulas y profesores
        if len(group.classroom_x_group) != len(
            reference_group.classroom_x_group
        ) or len(group.group_x_professor) != len(reference_group.group_x_professor):
            return "groups are not mirrors"

        # Validar mainSchedule de aulas
        for i in range(len(reference_group.classroom_x_group)):
            if (
                group.classroom_x_group[i].mainSchedule
                != reference_group.classroom_x_group[i].mainSchedule
            ):
                return "groups are not mirrors"

        # Validar nombres de profesores
        for i in range(len(reference_group.group_x_professor)):
            if (
                group.group_x_professor[i].professor.name
                != reference_group.group_x_professor[i].professor.name
            ):
                return "groups are not mirrors"

        # Validar subject
        if group.subject.name != reference_group.subject.name:
            return "groups are not mirrors"

        # Validar modalidad
        if group.modality != reference_group.modality:
            return "groups are not mirrors"

    # Si todos los grupos pasaron las validaciones
    # Puedes aplicar la actualización aquí a todos menos al primero
    for group in groups[1:]:
        await database.group.update(
            data={"mirrorGroupId": reference_group.mirrorGroupId},
            where={"id": group.id},
        )

    return "groups marked as mirror"

async def get_groups_same_subeject(schedule_pensum_ids: list[int], groupid: int):
    group = await database.group.find_first(
        where={"id": groupid},
        include={
            'subject': True
        }
    )
    subjects = await database.subject.find_many(where={"name": group.subject.name})
    subject_ids = [s.id for s in subjects]
    return await database.group.find_many(
        where={
            "academicSchedulePensumId": {"in": schedule_pensum_ids},
            "subjectId": {"in": subject_ids}
        },
        include={
            'classroom_x_group': True
        }
    )
 
async def get_groups_same_level(schedule_pensum_ids: list[int], groupid: int):
    group = await database.group.find_first(
        where={"id": groupid},
        include={
            'subject': True
        }
    )
    subjects = await database.subject.find_many(where={"level": group.subject.level})
    subject_ids = [s.id for s in subjects]
    return await database.group.find_many(
        where={
            "academicSchedulePensumId": {"in": schedule_pensum_ids},
            "subjectId": {"in": subject_ids}
        },
        include={
            'subject': True,
            'classroom_x_group': True
        }
    )

async def analyze_schedule_conflict_groups(schedule_pensum_ids: list[int]):
    groups = await database.group.find_many(
        where={
            "academicSchedulePensumId": {"in": schedule_pensum_ids}
        },
        include={
            "subject": True,  
            'classroom_x_group': True
        }
    )

    from collections import defaultdict
    from typing import Dict, List, Any

    grouped_by_name: Dict[str, List[Dict]] = defaultdict(list)
    grouped_by_level: Dict[int, List[Dict]] = defaultdict(list)

    for group in groups:
        if not group.subject or group.code == 0:
            continue
        name = group.subject.name
        level = group.subject.level
        schedules = []
        for cxg in group.classroom_x_group:
            schedules += extract_schedules(cxg.mainSchedule)

        data = {
            "id": group.id,
            "code": group.code,
            "schedules": schedules,
            "mirror_group_id": group.mirrorGroupId,
            "name": name  
        }

        grouped_by_name[name].append(data)
        grouped_by_level[level].append(data)

    conflicts = []

    def detect_conflicts(grouped: Dict[str | int, List[Dict[str, Any]]], type_: str):
        for key, group_list in grouped.items():
            for i in range(len(group_list)):
                for j in range(i + 1, len(group_list)):
                    groupA = group_list[i]
                    groupB = group_list[j]

                    if groupA["mirror_group_id"] is not None and groupA["mirror_group_id"] == groupB["mirror_group_id"]:
                        continue

                    set_i = set(groupA["schedules"])
                    set_j = set(groupB["schedules"])
                    overlap = set_i.intersection(set_j)

                    if overlap:
                        conflicts.append({
                            "type": type_,
                            "key": key,
                            "groupA_id": groupA["id"],
                            "groupA_code": groupA["code"],
                            "groupA_name": groupA["name"],  
                            "groupB_id": groupB["id"],
                            "groupB_code": groupB["code"],
                            "groupB_name": groupB["name"],  
                            "conflicting_schedules": sorted(list(overlap))
                        })

    detect_conflicts(grouped_by_name, type_="name")
    detect_conflicts(grouped_by_level, type_="level")

    return conflicts


async def get_groups_to_export(schedule_pensum_id: int):
    groups = await database.group.find_many(
        where={
            "academicSchedulePensumId": schedule_pensum_id,
            "code": {
                "not": 0
            }
        },
        include={
            "classroom_x_group": {
                "include": {
                    "mainClassroom": True,
                    "auxClassroom": True,
                }
            },
            "group_x_professor": {"include": {"professor": True}},
            "mirror_group": True,
            "subject": {"include": {"pensum": {"include": {"academic_program": True}}}},
        },
        order=[
            {"subject": {"level": "asc"}},
            {"subject": {"name": "asc"}},
            {"code": "asc"},
        ],
    )
    return groups
