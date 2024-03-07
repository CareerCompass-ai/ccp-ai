from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

from pydantic.types import conint

class PostBase(BaseModel):
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
        orm_mode = True

