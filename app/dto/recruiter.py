from datetime import datetime
from typing import List, Optional

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

class TalentSavedResponse(BaseModel):
    candidate_id: int
    year_of_experience: Optional[int] = None
    open_to_work: Optional[bool] = None
    self_introduction: Optional[str] = None
    level: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    work_title: Optional[str] = None
    gender: Optional[bool] = None
    dob: Optional[datetime] = None
    detailed_address: Optional[str] = None
    city_name: Optional[str] = None
    country_name: Optional[str] = None

class ListTalentSavedResponse(BaseModel):
    records: List[TalentSavedResponse]