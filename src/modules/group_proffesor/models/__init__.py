from pydantic import BaseModel

class ProfessorResponse(BaseModel):
    id: int
    name: str
    identification: str

class GroupProfessor(BaseModel):
    professor: ProfessorResponse

class GroupProfessorRequest(BaseModel):
    professorId: int
    groupId: int

class ProfessorRequest(BaseModel):
    identification: str
    name: str