from pydantic import BaseModel, Field
from typing import Optional

class GroupRequest(BaseModel):
    code: int = Field(..., title="Group Code", description="The unique code of the group")
    groupSize: int = Field(..., title="Group Size", description="The size of the group")
    modality: str = Field(..., title="Modality", description="The modality of the group (e.g., online, in-person)")
    subjectId: int = Field(..., title="Subject ID", description="The ID of the subject associated with the group")
    academicSchedulePensumId: int = Field(..., title="Academic Schedule ID", description="The ID of the academic schedule associated with the group")
    mirrorGroupId: Optional[int] = Field(None, title="Mirror Group ID", description="The ID of the mirror group associated with the group")