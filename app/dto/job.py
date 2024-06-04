from fastapi import UploadFile, File, Form
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

class JobBase(BaseModel):
    id: Optional[int] = None
    job_title: Optional[str] = ""
    content: Optional[str] = ""
    content_url: Optional[str] = ""
    is_hiring: Optional[bool] = True
    opened_date: Optional[datetime] = None
    closed_date: Optional[datetime] = None
    salary_from: Optional[float] = 0.0
    salary_to: Optional[float] = 0.0
    job_type: Optional[str] = ""
    company_type: Optional[str] = ""
    address_id: Optional[int] = None
    applied_count: Optional[int] = 0
    hiring_level: Optional[str] = ""
    work_place: Optional[str] = ""
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    work_place: Optional[str] = ""
    common_job_title: Optional[str] = ""
    recruiter_id: Optional[int] = None
    file_name: Optional[str] = None
    display_content: Optional[str] = None

class ListJobRequest(BaseModel):
    page: Optional[int]
    size: Optional[int]
    input: Optional[str] = None
    job_type: Optional[str] = None
    company_type: Optional[str] = None
    last_updated: Optional[str] = None
    vectors: Optional[list[float]] = None
    salary_from: Optional[float] = None
    salary_to: Optional[float] = None
    hiring_level: Optional[str] = None
    work_place: Optional[str] = None
    applied_count: Optional[int] = None
    job_tags: Optional[str] = None
    city_name: Optional[str] = None
    country_name: Optional[str] = None
    salary: Optional[str] = None
    alpha: Optional[float] = None
    is_hiring: Optional[bool] = None
    latest_job_id: Optional[int] = None

class ListRelatedJobRequest(BaseModel):
    page: Optional[int]
    size: Optional[int]
    job_id: Optional[int]

class JobAggregate(JobBase):
    matching_score: Optional[float] = 0.0
    s_content: Optional[str] = ""
    combined_content: Optional[str] = ""
    address: Optional[str] = ""
    city_name: Optional[str] = ""
    country_name: Optional[str] = ""
    job_tags: list[str] = ""
    recruiter_id: Optional[int] = 0
    recruiter_name: Optional[str] = ""
    is_applied: Optional[bool] = False
    is_saved: Optional[bool] = False

class DynamicFilterCommonField(BaseModel):
    name: Optional[str]
    count: Optional[int]

class DynamicFilters(BaseModel):
    hiring_levels: List[DynamicFilterCommonField] = []
    job_types: List[DynamicFilterCommonField] = []
    work_places: List[DynamicFilterCommonField] = []
    company_types: List[DynamicFilterCommonField] = []

class ListJobResponse(BaseModel):
    count: int
    page: int
    size: int
    records: List[JobAggregate]
    dynamic_filters: DynamicFilters = DynamicFilters()

class ListRelatedJobResponse(BaseModel):
    page: int
    size: int
    records: List[JobAggregate]

class GetJobRequest(BaseModel):
    id: Optional[int] = None

class CreateJobPostRequest(BaseModel):
    file: UploadFile = File(...)
    hiring_level: str = Form(...)

class CreateJobPostResponse(BaseModel):
    message: str = "Job posted successfully"

class UploadJobMinioRequest(BaseModel):
    temp_path: str
    file_name: str
class UploadJobMinioResponse(BaseModel):
    url: str 

class ApplyJobRequest(BaseModel):
    resume_id: int
    job_id: int

class ApplyJobResponse(BaseModel):
    message: str = "Applied successfully"

class CloseJobRequest(BaseModel):
    job_id: int

class CloseJobResponse(BaseModel):
    message: str = "Job closed successfully"