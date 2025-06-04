from pydantic import BaseModel, Field
from typing import Optional

class ProfessorResponse(BaseModel):
    id: int
    name: str
    identification: str

class GroupProfessor(BaseModel):
    professor: ProfessorResponse