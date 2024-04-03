from typing import List, Optional
from pydantic import BaseModel, EmailStr
from datetime import datetime

class TagBase(BaseModel):
    id: int
    tag_name: str
    created_at: datetime
    updated_at: datetime

class Tag(BaseModel):
    id: int
    tag_name: str

class ListTagResponse(BaseModel):
    tags: List[Tag]
