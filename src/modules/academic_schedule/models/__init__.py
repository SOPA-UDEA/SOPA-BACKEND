from pydantic import BaseModel, Field
from typing import List

class ScheduleRequest(BaseModel):
    semester: str = Field(min_length=4, max_length=150)
    pensumsIds: List[int]

class ScheduleResponse(BaseModel):
    id: int
    semester: str
class ScheduleCreateResponse(BaseModel):
    id: int
    semester: str
    schedule_pensum_ids: list[int]

class ScheduleRequestDrai(BaseModel):
    semester: str = Field(min_length=4, max_length=150)
    pensumId: int

class AcademicSchedulePensumIdRequest(BaseModel):
    academicScheduleId: int
    pensumId: int 