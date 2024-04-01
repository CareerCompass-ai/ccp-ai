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
    applied_count: Optional[int] = None
    hiring_level: Optional[str] = None
    work_place: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    work_place: Optional[str] = None

class ListJobRequest(BaseModel):
    page: Optional[int]
    size: Optional[int]
    input: Optional[str] = None
    job_type: Optional[str] = None
    company_type: Optional[str] = None
    location: Optional[str] = None
    last_updated: Optional[str] = None
    vectors: Optional[list[float]] = None
    salary_from: Optional[float] = None
    salary_to: Optional[float] = None
    hiring_level: Optional[list[str]] = None
    work_place: Optional[list[str]] = None
    applied_count: Optional[int] = None
    job_tags: Optional[list[str]] = None
    city_name: Optional[int] = None
    country_name: Optional[int] = None

    # For vector search: search_type = "vector"
    # For full-text search: search_type = "fulltext"
    search_type: Optional[str] = None 

class JobAggregate(JobBase):
    matching_score: Optional[float] = None
    s_content: Optional[str] = None
    address: Optional[str] = None
    city_name: Optional[str] = None
    country_name: Optional[str] = None
    job_tags: list[str] = None
    recruiter_id: Optional[int] = None
    recruiter_name: Optional[str] = None

class ListJobResponse(BaseModel):
    count: int
    page: int
    size: int
    records: List[JobAggregate]

class GetJobRequest(BaseModel):
    id: Optional[int] = None
