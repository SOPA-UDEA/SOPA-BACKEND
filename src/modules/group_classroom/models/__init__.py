from pydantic import BaseModel, Field
from typing import Optional

class GroupClassroomRequest(BaseModel):
    groupId: int = Field(..., description="ID of the group")
    mainClassroomId: int = Field(..., description="ID of the classroom")
    auxClassroomId: Optional[int] = Field(None, description="ID of the auxiliary classroom")
    mainSchedule: str = Field(..., description="Main schedule of the group")
    auxSchedule: Optional[str] = Field(None, description="Auxiliary schedule ID")

class MessageGroupClassroomRequest(BaseModel):
    groupId: int = Field(..., description="ID of the classroom group")
    messageTypeId: int = Field(..., description="ID of the message type")
    
