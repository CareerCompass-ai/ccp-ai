from typing import List, Optional
from pydantic import BaseModel, EmailStr
from datetime import datetime

class ResumeBase(BaseModel):
    id: Optional[int] = None
    candidate_id: Optional[int] = None
    content: Optional[str] = None
    resume_link: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class ResumeAggregate(ResumeBase):
    matching_score: Optional[float] = None
    candidate_name: Optional[str] = None
    work_title: Optional[str] = None
    open_to_work: Optional[bool] = None
    level: Optional[str] = None
    candidate_address: Optional[str] = None
    s_content: Optional[str] = None
    skills: list[str] = None
    applied_jobs: list[int] = None

class ListResumeRequest(BaseModel):
    page: Optional[int] = None
    size: Optional[int] = None
    job_id: Optional[int] = None

class ListResumeResponse(BaseModel):
    count: int = None
    page: int
    size: int
    records: List[ResumeAggregate] = None

class ResumeurlRequest(BaseModel):
    resume_name: Optional[str]
    resume_path: Optional[str] 
class ResumeResponse_Url(BaseModel):
    resume_name: str = None
    bucket_name: str = None
    minio_resume_link: str = None

