from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class ViewJobBase(BaseModel):
    candidate_id: Optional[int] = None
    job_id: Optional[int] = None
    view_datetime: Optional[datetime] = None

    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

