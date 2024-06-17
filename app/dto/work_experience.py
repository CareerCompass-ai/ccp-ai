from datetime import datetime, date
from typing import Optional

from pydantic import BaseModel


class WorkExperienceBase(BaseModel):
    id: int
    candidate_id: Optional[int] = None
    work_title: Optional[str] = ""
    company_id: Optional[int] = ""
    company_name: Optional[str] = ""
    startdate: Optional[date] = ""
    enddate: Optional[date] = ""
    is_engaged: Optional[bool] = ""
    detail: Optional[str] = ""
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None