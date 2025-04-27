from pydantic import BaseModel
from typing import Optional, Dict

class SubjectRequest(BaseModel):
    level: int
    fields: dict
    code: str
    credits: int
    weeklyHours: int
    weeks: int
    enableable: bool
    validable: bool
    preRequirements: Optional[Dict] = None
    coRequirements: Optional[Dict] = None
    creditRequirements: Optional[str] = None
    name: str
    pensumId: int