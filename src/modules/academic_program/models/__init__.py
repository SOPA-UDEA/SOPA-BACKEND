from pydantic import BaseModel


class AcademicProgramResponse(BaseModel):
    modalityAcademic: str

