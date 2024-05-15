from typing import Optional
from pydantic import BaseModel
from datetime import datetime

class ApplicationBase(BaseModel):
    resume_id: Optional[int] = None
    job_id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
class ListJobResponse(BaseModel):
    applied_jobs: list[int] = None