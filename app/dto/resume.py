from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel

from app.dto.certificate import CertificateBase
from app.dto.education import EducationBase
from app.dto.project import ProjectBase
from app.dto.work_experience import WorkExperienceBase


class ResumeBase(BaseModel):
    id: Optional[int] = None
    candidate_id: Optional[int] = None
    content: Optional[str] = None
    resume_link: Optional[str] = None
    resume_name: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    active: bool = True

class ResumeAggregate(ResumeBase):
    matching_score: Optional[float] = None
    candidate_name: Optional[str] = None
    work_title: Optional[str] = None
    open_to_work: Optional[bool] = None
    level: Optional[str] = None
    candidate_address: Optional[str] = None
    s_content: Optional[str] = None
    content: Optional[str] = None
    skills: list[str] = None
    applied_jobs: list[int] = None
    projects: List[ProjectBase] = None
    certificates: List[CertificateBase] = None
    educations: List[EducationBase] = None
    work_expericences: List[WorkExperienceBase] = None

class ListResumeRequest(BaseModel):
    page: Optional[int] = None
    size: Optional[int] = None
    job_id: Optional[int] = None

class ListResumeResponse(BaseModel):
    count: int = None
    page: int
    size: int
    records: List[ResumeAggregate] = None

class UploadResumeMinioRequest(BaseModel):
    temp_path: str
    file_name: str
class UploadResumeMinioResponse(BaseModel):
    url: str

class ContentResponse(BaseModel):
    content: Optional[str] = None

class ResumeRequest(BaseModel):
    candidate_id: Optional[int] = None
    content: Optional[str] = None
    resume_link: Optional[str] = None
    resume_name: Optional[str] = None

class CreateResumePostResponse(BaseModel):
    message: str = "Resume post created successfully"

class GetResumesOfCandidateResponse(BaseModel):
    records: List[ResumeBase]

class DeleteResumeResponse(BaseModel):
    msg: str

class DeleteResumeRequest(BaseModel):
    resume_id: str
