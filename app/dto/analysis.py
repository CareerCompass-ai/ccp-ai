from typing import List
from pydantic import BaseModel
from datetime import datetime

class TopJobTitlesResponse(BaseModel):
    job_title: str
    count: int

class ListTopJobTitlesResponse(BaseModel):
    data: List[TopJobTitlesResponse]

class GetTopJobTitlesSalaryResponse(BaseModel):
    job_title: str
    hiring_level: str
    average_salary: float

class ListTopJobTitlesSalaryResponse(BaseModel):
    data: List[GetTopJobTitlesSalaryResponse]

class GetTopAppliedJobTitlesResponse(BaseModel):
    job_title: str
    count: int

class ListTopAppliedJobTitlesResponse(BaseModel):
    data: List[GetTopAppliedJobTitlesResponse]

class TopSkillResponse(BaseModel):
    skill: str
    id: int
    count: int

class GetTopSkillResponse(BaseModel):
    data: List[TopSkillResponse]

class NumberOfCompanyTypeResponse(BaseModel):
    company_type: str
    count: int

class GetNumberOfCompanyTypeResponse(BaseModel):
    data: List[NumberOfCompanyTypeResponse]

class NumberOfNewUser(BaseModel):
    id: int
    role: str
    created_at: datetime
class GetNumberOfNewUser(BaseModel):
    data: List[NumberOfNewUser]

class NumberOfAllNewUser(BaseModel):
    role: str
    count: int

class GetNumberOfAllNewUser(BaseModel):
    data: List[NumberOfAllNewUser]

class NumberOfJobStatus(BaseModel):
    status: bool
    count: int
class GetNumberOfJobStatus(BaseModel):
    data: List[NumberOfJobStatus]

class TopRecruiterJobPosting(BaseModel):
    recruiter_id: int
    full_name: str
    count: int

class GetTopRecruiterJobPosting(BaseModel):
    data: List[TopRecruiterJobPosting]

class TopViewedJob(BaseModel):
    job_title: str
    count: int

class GetTopViewedJob(BaseModel):
    data: List[TopViewedJob]

class TopWorkTitlesResponse(BaseModel):
    work_title: str
    count: int

class ListTopWorkTitlesResponse(BaseModel):
    data: List[TopWorkTitlesResponse]

class ChangeJobSalaryResponse(BaseModel):
    time: datetime
    job_title: str
    salary: float

class ChangeJobSalaryByYearResponse(BaseModel):
    time: datetime
    job_title: str
    hiring_level: str
    average_salary: float

class ListChangeJobSalaryByYearResponse(BaseModel):
    data: List[ChangeJobSalaryByYearResponse]

class ListChangeJobSalaryResponse(BaseModel):
    data: List[ChangeJobSalaryResponse]

class NumberofJobsByCountryResponse(BaseModel):
    hiring_level: str
    city: str
    count: int

class ListNumberofJobsByCountryResponse(BaseModel):
    data: List[NumberofJobsByCountryResponse]

class Country(BaseModel):
    country_name: str

class ListCountryName(BaseModel):
    data: List[Country]