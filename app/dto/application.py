from typing import List, Optional
from pydantic import BaseModel

class ListJobResponse(BaseModel):
    applied_jobs: list[int] = None