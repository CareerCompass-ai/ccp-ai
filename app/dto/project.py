from datetime import datetime, date
from typing import Optional

from pydantic import BaseModel


class ProjectBase(BaseModel):
    id: int
    candidate_id: Optional[int] = None
    project_name: Optional[str] = ""
    startdate: Optional[date] = ""
    enddate: Optional[date] = ""
    is_working: Optional[bool] = False
    detail: Optional[str] = ""
    created_at: Optional[datetime] = ""
    updated_at: Optional[datetime] = ""