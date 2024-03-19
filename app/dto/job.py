from typing import List, Optional
from pydantic import BaseModel, EmailStr, ValidationError
from datetime import datetime

class JobBase(BaseModel):
    id: Optional[int] = None
    job_title: Optional[str] = None
    content: Optional[str] = None
    content_url: Optional[str] = None
    is_hiring: Optional[bool] = None
    opened_date: Optional[datetime] = None
    closed_date: Optional[datetime] = None
    salary_from: Optional[float] = None
    salary_to: Optional[float] = None
    job_type: Optional[str] = None
    company_type: Optional[str] = None
    address_id: Optional[int] = None

    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class ListJobRequest(BaseModel):
    page: Optional[int]
    size: Optional[int]
    input: Optional[str] = None
    vectors: Optional[List[List[float]]] = None
    salary_from: Optional[float] = None
    salary_to: Optional[float] = None
    experience_level: Optional[int] = None
    type: Optional[int] = None
    working_model: Optional[int] = None
    location: Optional[str] = None
    last_updated: Optional[str] = None

class JobAggregate(JobBase):
    matching_score: Optional[float] = None
    user_id: Optional[int] = None
    user_name: Optional[str] = None
    address: Optional[str] = None
    job_tags: list[str] = None
    recruiter_id: Optional[int] = None

class ListJobResponse(BaseModel):
    count: int
    page: int
    size: int
    records: List[JobAggregate]
