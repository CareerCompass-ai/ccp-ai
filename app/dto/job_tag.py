from typing import List, Optional
from pydantic import BaseModel, EmailStr
from datetime import datetime

class JobTagsBase(BaseModel):
    tag_id: Optional[int] = None
    job_id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class ListJobTagsResponse(BaseModel):
    tags: List[JobTagsBase]
