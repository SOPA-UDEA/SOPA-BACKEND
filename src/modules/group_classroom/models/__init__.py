from pydantic import BaseModel, Field
from typing import Optional
from src.modules.classroom.models import Classroom


class GroupClassroomRequest(BaseModel):
    groupId: int = Field(..., description="ID of the group")
    mainClassroomId: int = Field(..., description="ID of the classroom")
    auxClassroomId: Optional[int] = Field(
        None, description="ID of the auxiliary classroom"
    )
    mainSchedule: str = Field(..., description="Main schedule of the group")
    auxSchedule: Optional[str] = Field(None, description="Auxiliary schedule ID")


class GroupClassroomResponse(BaseModel):
    id: int
    groupId: int
    mainClassroomId: int
    auxClassroomId: Optional[int]
    mainSchedule: str
    auxSchedule: Optional[str]
    mainClassroom: Classroom
    auxClassroom: Optional[Classroom] = None


class MessageGroupClassroomRequest(BaseModel):
    groupId: int = Field(..., description="ID of the classroom group")
    messageTypeId: int = Field(..., description="ID of the message type")
    detail: Optional[str] = Field(None, description="Details of the message")


class GroupClassroomRequestAux(BaseModel):
    auxClassroomId: int = Field(..., description="ID of the auxiliary classroom")
    auxSchedule: str = Field(..., description="Auxiliary schedule ID")


class CollisionRequest(BaseModel):
    semester: str = Field(..., description="Semester to check for collisions")


class MessageTypeResponse(BaseModel):
    id: int
    name: str = Field(..., description="Name of the message type")


class GroupNotificationResponse(BaseModel):
    id: int
    messageTypeId: int
    detail: Optional[str] = Field(None, description="Details of the message")
    groupId: int
    messageType: MessageTypeResponse
