from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

class AssistantBase(BaseModel):
    id: Optional[int] = None
    assistant_id: str
    thread_id: str
    file_id: str
    assistant_name: Optional[str] = ""
    file_name: Optional[str] = ""
    file_url: Optional[str] = ""
    time_from: Optional[datetime] = None
    time_to: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


