from fastapi import UploadFile, File, Form
from typing import List, Optional
from pydantic import BaseModel, Field, EmailStr, ValidationError
from datetime import datetime

class GetTopJobTitlesResponse(BaseModel):
    job_title: str
    count: int

class GetTopSkillResponse(BaseModel):
    skill: str
    count: int

class GetNumberOfCompanyTypeResponse(BaseModel):
    company_type: str
    count: int

class GetNumberOfNewUser(BaseModel):
    role: str
    created_at: datetime

class GetNumberOfJobStatus(BaseModel):
    status: str
    count: int