from typing import List
from pydantic import BaseModel, Field

from src.modules.subject.schemas import ClassroomXGroupResponse, SubjectResponse

class GroupRequest(BaseModel):
    groupSize: int 
    modality: str 
    code: int 
    mirrorGroupId: int
    subjectId: int 
    academicSchedulePensumId: int
    maxSize: int
    registeredPlaces: int

class AcademicSchedulePensumRequest(BaseModel):
    pensumId: int = Field(gt=0)
    academicScheduleId: int = Field(gt=0)

class MirrorGroupRequest(BaseModel):
    name: str

class GroupCreationRequest(BaseModel):
    group: GroupRequest
    mirror: MirrorGroupRequest
    academic: AcademicSchedulePensumRequest

class MirrorGroupResponse(BaseModel):
    id: int
    name: str

class GroupResponse(BaseModel):
    id: int
    groupSize: int
    modality: str 
    code: int 
    mirrorGroupId: int 
    subjectId: int 
    academicSchedulePensumId: int
    mirror_group: MirrorGroupResponse
    subject: SubjectResponse
    maxSize: int
    registeredPlaces: int
    classroom_x_group: List[ClassroomXGroupResponse]