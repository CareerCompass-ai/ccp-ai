from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class TagBase(BaseModel):
    id: int
    tag_name: str
    created_at: datetime
    updated_at: datetime

class Tag(BaseModel):
    id: Optional[int] = None
    tag_name: str

class ListTagResponse(BaseModel):
    tags: List[Tag]
