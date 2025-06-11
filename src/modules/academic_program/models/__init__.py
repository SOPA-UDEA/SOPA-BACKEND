from pydantic import BaseModel


class AcademicProgramResponse(BaseModel):
    name: str
    modalityAcademic: str

