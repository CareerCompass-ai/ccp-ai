from datetime import datetime
from typing import List, Optional
from app.dto.certificate import CertificateBase
from app.dto.education import EducationBase
from app.dto.project import ProjectBase
from app.dto.work_experience import WorkExperienceBase
from pydantic import BaseModel
class SaveTalentRequest(BaseModel):
    recruiter_id: int
    candidate_id: int
    resume_id: int
    type: int #1: save, 2: unsave

class SaveTalentResponse(BaseModel):
    msg: str
