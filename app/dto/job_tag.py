from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class JobTagsBase(BaseModel):
    tag_id: Optional[int] = None
    job_id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class ListJobTagsResponse(BaseModel):
    tags: List[JobTagsBase]
