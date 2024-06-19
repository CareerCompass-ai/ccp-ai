from datetime import datetime
from typing import List, Optional
from app.dto.certificate import CertificateBase
from app.dto.education import EducationBase
from app.dto.project import ProjectBase
from app.dto.work_experience import WorkExperienceBase
from pydantic import BaseModel
class JobPostedResponse(BaseModel):
    job_id: int
    job_title: Optional[str] = None
    content: Optional[str] = ""
    is_hiring: Optional[bool] = None
    opened_date: Optional[datetime] = None
    closed_date: Optional[datetime] = None
    salary_from: Optional[float] = 0.0
    salary_to: Optional[float] = 0.0
    job_type: Optional[str] = ""
    work_place: Optional[str] = ""
    company_type: Optional[str] = ""
    hiring_level: Optional[str] = ""
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    applied_count: int
    display_content: Optional[str] = ""

class ListJobsPostedResponse(BaseModel):
    records: List[JobPostedResponse]

class SaveTalentRequest(BaseModel):
    recruiter_id: int
    candidate_id: int
    resume_id: int
    type: int #1: save, 2: unsave

class SaveTalentResponse(BaseModel):
    msg: str

class GetTalentSavedResponse(BaseModel):
    id: int
    candidate_id: int
    candidate_name: Optional[str] = None
    year_of_experience: Optional[int] = None
    open_to_work: Optional[bool] = None
    level: Optional[str] = None
    work_title: Optional[str] = None
    candidate_address: Optional[str] = None
    content: Optional[str] = None
    s_content: Optional[str] = None
    resume_link: Optional[str] = None
    skills: List[str] = None
    projects: List[ProjectBase] = None
    certificates: List[CertificateBase] = None
    educations: List[EducationBase] = None
    work_expericences: List[WorkExperienceBase] = None

class ListIdTalentSavedResponse(BaseModel):
    ids: List[int]

class ListTalentSavedResponse(BaseModel):
    records: List[GetTalentSavedResponse]
