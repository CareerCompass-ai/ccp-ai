from typing import List, Optional
from pydantic import BaseModel, EmailStr
from datetime import datetime

class JobTagsBase(BaseModel):
    tag_id: int
    job_id: int
    created_at: datetime
    updated_at: datetime

class ListJobTagsResponse(BaseModel):
    tags: List[JobTagsBase]
