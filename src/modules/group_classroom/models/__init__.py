from pydantic import BaseModel


class GroupClassroomRequest(BaseModel):
    groupId: int
    classroomId: int
    scheduleId: str


class ClassroomSchedulesRequest(BaseModel):
    classroomId: int
    days: list[str]
