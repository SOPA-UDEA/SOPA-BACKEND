from pydantic import BaseModel, Field

class Classroom(BaseModel):
    id: int = Field(..., description="Unique identifier for the classroom")
    capacity: int = Field(..., gt=0, description="Maximum number of students in the classroom")
    location: str = Field(..., max_length=255, description="Location of the classroom")
    ownDepartment: bool = Field(..., description="Indicates if the classroom is owned by the department")
    virtualMode: bool = Field(..., description="Indicates if the classroom is virtual")

class ClassroomRequest(BaseModel):
    capacity: int = Field(..., gt=0, description="Maximum number of students in the classroom")
    location: str = Field(..., max_length=255, description="Location of the classroom")
    ownDepartment: bool = Field(..., description="Indicates if the classroom is owned by the department")
    virtualMode: bool = Field(..., description="Indicates if the classroom is virtual")