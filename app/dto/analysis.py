from fastapi import UploadFile, File, Form
from typing import List, Optional
from pydantic import BaseModel, Field, EmailStr, ValidationError
from datetime import datetime

class GetTopJobTitlesResponse(BaseModel):
    job_title: str
    count: int

class ListTopJobTitlesResponse(BaseModel):
    records: List[GetTopJobTitlesResponse]

class GetTopJobTitlesSalaryResponse(BaseModel):
    id: int
    job_title: str
    job_type: str
    company_type: str
    work_place: str
    salary: float

class ListTopJobTitlesSalaryResponse(BaseModel):
    records: List[GetTopJobTitlesSalaryResponse]

class GetTopAppliedJobTitlesResponse(BaseModel):
    job_title: str
    count: int

class ListTopAppliedJobTitlesResponse(BaseModel):
    records: List[GetTopAppliedJobTitlesResponse]