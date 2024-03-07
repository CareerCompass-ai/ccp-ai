from typing import List, Optional
from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

from pydantic.types import conint

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

    class Config:
        from_attributes = True

class ListJobResponse(JobBase):
    # count: int
    # page: int
    # size: int
    # records: List[JobBase]
    pass
