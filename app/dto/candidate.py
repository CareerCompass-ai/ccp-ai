from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel
from app.dto.job import JobAggregate

class AppliedJobsResponse(JobAggregate):
    resume_id: int
    resume_url: str

class ListAppliedJobsResponse(BaseModel):
    count: int
    page: int
    size: int
    records: List[AppliedJobsResponse]
class ResumesAppliedResponse(BaseModel):
    job_id: int
    resume_id: int
    resume_url: str
class ListResumesAppliedResponse(BaseModel):
    records: List[ResumesAppliedResponse]
class UpdateSaveJobRequest(BaseModel):
    candidate_id: int
    job_id: int
    type: int #1: save, 2: unsave
class UpdateSaveJobResponse(BaseModel):
    message: str
class CreateJobViewedRequest(BaseModel):
    job_id: int
    candidate_id: int

class JobViewdResponse(BaseModel):
    message: Optional[str] = ""
    job_id: Optional[int] = None
    candidate_id: Optional[int] = None
    time: Optional[datetime] = None

class ListJobsSaved(BaseModel):
    count: int
    page: int
    size: int
    records: List[JobAggregate]