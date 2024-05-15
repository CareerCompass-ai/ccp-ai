from typing import Optional
from pydantic import BaseModel
from datetime import datetime

class WorkExperienceBase(BaseModel):
    id: int
    candidate_id: Optional[int] = None
    work_title: Optional[str] = ""
    company_id: Optional[int] = None
    company_name: Optional[str] = ""
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    is_engaged: Optional[bool] = None
    detail: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None