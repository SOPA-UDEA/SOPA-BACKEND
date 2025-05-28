from pydantic import BaseModel
from src.modules.pensum.models import PensumResponse

class SubjectResponse(BaseModel):
    id: int
    name: str
    level: int
    code: str
    pensum: PensumResponse

class ClassroomResponse(BaseModel):
    id: int
    location: str
    capacity: int

class ClassroomXGroupResponse(BaseModel):
    id: int
    mainSchedule: str
    # classroom_x_group_classroom_x_group_mainClassroomIdToclassroom: ClassroomResponse