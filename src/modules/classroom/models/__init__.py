from pydantic import BaseModel, Field
from typing import Optional

class Classroom(BaseModel):
    id: int = Field(..., description="Unique identifier for the classroom")
    capacity: Optional[int] = Field(None,description="Maximum number of students in the classroom")
    location: str = Field(..., max_length=255, description="Location of the classroom")
    ownDepartment: bool = Field(..., description="Indicates if the classroom is owned by the department")
    virtualMode: bool = Field(..., description="Indicates if the classroom is virtual")
    enabled: bool = Field(..., description="Indicates if the classroom is enabled")

class ClassroomRequest(BaseModel):
    capacity: Optional[int] = Field(None, description="Maximum number of students in the classroom")
    location: str = Field(..., max_length=255, description="Location of the classroom")
    ownDepartment: bool = Field(..., description="Indicates if the classroom is owned by the department")
    virtualMode: bool = Field(..., description="Indicates if the classroom is virtual")
    enabled: Optional[bool] = Field(None, description="Indicates if the classroom is enabled")

class EnableStatusRequest(BaseModel):
    enabled: bool = Field(..., description="Indicates if the classroom should be enabled or disabled")