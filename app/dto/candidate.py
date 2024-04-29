from fastapi import UploadFile, File, Form
from typing import List, Optional
from pydantic import BaseModel, EmailStr, ValidationError
from datetime import datetime

class AppliedJobsResponse(BaseModel):
    job_id: int
    resume_id: int
    job_title: str
    content: Optional[str] = ""
    is_hiring: Optional[bool] = None
    opened_date: Optional[datetime] = None
    closed_date: Optional[datetime] = None
    salary_from: Optional[float] = 0.0
    salary_to: Optional[float] = 0.0
    job_type: Optional[str] = ""
    work_place: Optional[str] = ""
    company_type: Optional[str] = ""
    hiring_level: Optional[str] = ""
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
    content: Optional[str] = ""
    is_hiring: Optional[bool] = None
    opened_date: Optional[datetime] = None
    closed_date: Optional[datetime] = None
    salary_from: Optional[float] = 0.0
    salary_to: Optional[float] = 0.0
    job_type: Optional[str] = ""
    work_place: Optional[str] = ""
    company_type: Optional[str] = ""
    hiring_level: Optional[str] = ""
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class ListSavedJobsResponse(BaseModel):
    records: List[SavedJobsResponse] = None