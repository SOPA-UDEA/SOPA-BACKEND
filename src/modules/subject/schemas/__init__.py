from pydantic import BaseModel, ConfigDict
from src.modules.pensum.models import PensumResponse
from typing import Optional

class SubjectResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    level: int
    code: str
    pensum: PensumResponse

class ClassroomResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    location: str
    capacity: Optional[int] = None

class ClassroomXGroupResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    mainSchedule: str
    mainClassroom: Optional[ClassroomResponse] = None
    auxClassroom: Optional[ClassroomResponse] = None
    auxSchedule: Optional[str] = None