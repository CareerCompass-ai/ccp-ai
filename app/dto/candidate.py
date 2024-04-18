from fastapi import UploadFile, File, Form
from typing import List, Optional
from pydantic import BaseModel, EmailStr, ValidationError
from datetime import datetime

class AppliedJobsResponse(BaseModel):
    job_id: int
    resume_id: int
    job_title: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class ListAppliedJobsResponse(BaseModel):
    records: List[AppliedJobsResponse] = None

class UpdateSaveJobRequest(BaseModel):
    candidate_id: int
    job_id: int
    type: int #1: save, 2: unsave
class UpdateSaveJobResponse(BaseModel):
    message: str

class SavedJobsResponse(BaseModel):
    job_id: int
    job_title: str

class ListSavedJobsResponse(BaseModel):
    records: List[SavedJobsResponse] = None