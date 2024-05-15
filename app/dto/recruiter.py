from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

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

class ListJobsPostedResponse(BaseModel):
    records: List[JobPostedResponse]