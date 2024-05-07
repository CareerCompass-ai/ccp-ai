from typing import List, Optional
from pydantic import BaseModel, EmailStr, ValidationError
from datetime import datetime

class ViewJobBase(BaseModel):
    candidate_id: Optional[int] = None
    job_id: Optional[int] = None
    viewed_datetime: Optional[datetime] = None

    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

