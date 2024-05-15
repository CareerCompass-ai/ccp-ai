from typing import Optional
from pydantic import BaseModel
from datetime import datetime

class ViewJobBase(BaseModel):
    candidate_id: Optional[int] = None
    job_id: Optional[int] = None
    view_datetime: Optional[datetime] = None

    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

