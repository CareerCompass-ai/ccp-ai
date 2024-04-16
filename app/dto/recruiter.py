from fastapi import UploadFile, File, Form
from typing import List, Optional
from pydantic import BaseModel, EmailStr, ValidationError
from datetime import datetime

class JobPostedResponse(BaseModel):
    job_id: int
    job_title: Optional[str] = None
    created_at: Optional[datetime] = None
    closed_date: Optional[datetime] = None
    applied_count: int

class ListJobsPostedResponse(BaseModel):
    record: List[JobPostedResponse]