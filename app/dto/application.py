from fastapi import UploadFile, File, Form
from typing import List, Optional
from pydantic import BaseModel, EmailStr, ValidationError
from datetime import datetime

class ApplicationBase(BaseModel):
    resume_id: Optional[int] = None
    job_id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
class ListJobResponse(BaseModel):
    applied_jobs: list[int] = None