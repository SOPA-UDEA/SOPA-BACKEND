from pydantic import BaseModel

from src.modules.academic_program.models import AcademicProgramResponse


class PensumResponse(BaseModel):
    version: int
    academic_program: AcademicProgramResponse