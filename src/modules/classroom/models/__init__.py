from pydantic import BaseModel


class ClassroomRequest(BaseModel):
    capacity: int
    location: str
    ownDepartment: bool
    virtualMode: bool
