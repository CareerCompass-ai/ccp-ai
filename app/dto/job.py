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
    matching_score: float
    user_id: int

class ListJobResponse(BaseModel):
    count: int
    page: int
    size: int
    records: List[JobAggregate]
