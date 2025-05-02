from pydantic import BaseModel


class GroupRequest(BaseModel):
    groupSize: int
    modality: str
    code: int
    mirrorGroupId: int
    subjectId: int
    academicScheduleId: int
