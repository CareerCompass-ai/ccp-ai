from fastapi import status, HTTPException, Depends, APIRouter, Query

from app.dto import analysis

from app.repo.analysis_repo import AnalysisRepository

from  typing import List

import constant.common as constant

analysis_router = APIRouter(
    prefix="/api",
    tags=['Analysis']
)

analysis_repo = AnalysisRepository()

@analysis_router.get("/analysis/top-job-titles", response_model=List[analysis.GetTopJobTitlesResponse])
def list_top_job_titles(
    month: int = Query(None, description="Month"),
    year: int = Query(None, description="Year"),
):
    try:
        data = analysis_repo.get_top_job_titles(month=month, year=year)
        return data
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    

@analysis_router.get("/analysis/top-skills", response_model=List[analysis.GetTopSkillResponse])
def list_top_skills(
    top_number: int = Query(None, description="Top number of skills")
):
    try:
        data = analysis_repo.get_top_skills(top_number=top_number)
        return data
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    
@analysis_router.get("/analysis/job-company-type", response_model=List[analysis.GetNumberOfCompanyTypeResponse])
def get_number_of_company_type():
    try:
        data = analysis_repo.number_of_company_type()
        return data
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    
@analysis_router.get("/analysis/new-user-in-time-range", response_model=List[analysis.GetNumberOfNewUser])
def list_new_user_in_time_range(
    time_from: str = Query(None, description="Start time to calculate number of new users"),
    time_to: str = Query(None, description="End time to calculate number of new users")
):
    try:
        data = analysis_repo.get_number_of_new_user(time_from=time_from, time_to=time_to)
        return data
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    
@analysis_router.get("/analysis/count-user-by-role", response_model=List[analysis.GetNumberOfAllNewUser])
def count_new_user_by_role(
):
    try:
        data = analysis_repo.count_all_number_of_user_by_role()
        return data
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    
@analysis_router.get("/analysis/job-status", response_model=List[analysis.GetNumberOfJobStatus])
def percentage_of_different_job_status(
):
    try:
        data = analysis_repo.percentage_of_different_job_status()
        return data
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@analysis_router.get("/analysis/top-recruiter-by-job-posting", response_model=List[analysis.GetTopRecruiterJobPosting])
def get_top_recruiters_job_posting(
    top_number: int = Query(None, description="Top number of recruiter"),
    time_from: str = Query(None, description="Start time to find out the top recruiter"),
    time_to: str = Query(None, description="End time to find out the top recruiter")
):
    try:
        data = analysis_repo.get_top_recruiters_job_posting(top_number, time_from, time_to)
        return data
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))