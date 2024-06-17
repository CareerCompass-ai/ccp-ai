from datetime import datetime, date
from typing import Optional

from pydantic import BaseModel


class EducationBase(BaseModel):
    id: int
    candidate_id: Optional[int] = None
    school_name: Optional[str] = ""
    major: Optional[str] = ""
    startdate: Optional[date] = ""
    enddate: Optional[date] = ""
    is_studying: Optional[bool] = ""
    detail: Optional[str] = ""
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None