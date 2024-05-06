from fastapi import UploadFile, File, Form
from typing import List, Optional
from pydantic import BaseModel, Field, EmailStr, ValidationError
from datetime import datetime

class GetTopJobTitlesResponse(BaseModel):
    job_title: str
    count: int

class GetTopSkillResponse(BaseModel):
    skill: str
    id: int
    count: int

class GetNumberOfCompanyTypeResponse(BaseModel):
    company_type: str
    count: int

class GetNumberOfNewUser(BaseModel):
    id: int
    role: str
    created_at: datetime

class GetNumberOfAllNewUser(BaseModel):
    role: str
    count: int


class GetNumberOfJobStatus(BaseModel):
    status: str
    count: int


class GetTopRecruiterJobPosting(BaseModel):
    recruiter_id: int
    full_name: str
    count: int
