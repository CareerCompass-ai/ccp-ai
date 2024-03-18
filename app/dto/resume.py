from typing import List, Optional
from pydantic import BaseModel, EmailStr
from datetime import datetime
class JobBase(BaseModel):
    id: int
    title: str
    content: str
    content_url: str
    is_hiring: bool
    opened_date: datetime
    closed_date: datetime
    salary_from: float
    salary_to: float
    job_type: int
    company_type: int

    created_at: datetime
    updated_at: datetime
    
class ResumeAggregate(JobBase):
    resume_id: int
    candidate_id: int
    user_id: int
    last_name: int
    first_name: int
    open_to_work: bool
    work_title: str
    content: str