from fastapi import UploadFile, File, Form
from typing import List, Optional
from pydantic import BaseModel, Field, EmailStr, ValidationError
from datetime import datetime

class GetTopJobTitlesResponse(BaseModel):
    job_title: str
    record: int

class GetTopJobTitlesSalaryResponse(BaseModel):
    id: int
    job_title: str
    job_type: str
    company_type: str
    work_place: str
    salary: float