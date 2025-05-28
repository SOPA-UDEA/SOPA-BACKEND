from pydantic import BaseModel

from src.modules.academic_program.models import AcademicProgramResponse


class PensumResponse(BaseModel):
    academic_program: AcademicProgramResponse