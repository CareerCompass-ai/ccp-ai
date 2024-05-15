from typing import Optional
from pydantic import BaseModel
from datetime import datetime

class EducationBase(BaseModel):
    id: int
    candidate_id: Optional[int] = None
    school_name: Optional[str] = ""
    major: Optional[str] = ""
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    is_studying: Optional[bool] = None
    detail: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None