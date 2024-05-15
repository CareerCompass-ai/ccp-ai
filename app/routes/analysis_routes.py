from fastapi import status, HTTPException, Depends, APIRouter, Query
from sqlalchemy.orm import Session
from app.dto import analysis

from app.repo.analysis_repo import AnalysisRepository

from  typing import List

from datetime import datetime

import constant.common as constant
from config.postgres import PostgresDB

from pkg.logging import logger

analysis_router = APIRouter(
    prefix="/api",
    tags=['Analysis']
)

analysis_repo = AnalysisRepository()

#1
@analysis_router.get("/analysis/top-job-titles", response_model=analysis.ListTopJobTitlesResponse)
async def list_top_job_titles(
    month: int = Query(None, description="Month"),
    year: int = Query(None, description="Year"),
    db: Session = Depends(PostgresDB.get_db)
):
    try:
        data = await analysis_repo.get_top_job_titles(db, month=month, year=year)
        return data
    except Exception as e:
        logger.error(f"error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str("Oops, sorry, our server went wrong"))
    
#5
@analysis_router.get("/analysis/top-job-titles-salary", response_model=analysis.ListTopJobTitlesSalaryResponse)
async def list_top_job_titles_salary(
    top: int = Query(None, description="Number of records"),
    level: str = Query(None, description="Hiring Level"),
    order_by: int = Query(None, description="1: desc and 2: asc"),
    db: Session = Depends(PostgresDB.get_db)
):
    try:
        data = await analysis_repo.get_top_leader_salaries(db, limit=top, hiring_level=level, order=order_by)
        return data
    except Exception as e:
        logger.error(f"error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str("Oops, sorry, our server went wrong"))
    
#6
@analysis_router.get("/analysis/top-applied-job-titles", response_model=analysis.ListTopAppliedJobTitlesResponse)
async def list_top_applied_job_titles(
    month: int = Query(None, description="Month"),
    year: int = Query(None, description="Year"),
    db: Session = Depends(PostgresDB.get_db)
):
    try:
        data = await analysis_repo.get_most_applied_job_titles(db, month=month, year=year)
        return data
    except Exception as e:
        logger.error(f"error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str("Oops, sorry, our server went wrong"))
    
@analysis_router.get("/analysis/top-skills", response_model=analysis.GetTopSkillResponse)
async def list_top_skills(
    top_number: int = Query(None, description="Top number of skills"),
    db: Session = Depends(PostgresDB.get_db)
):
    try:
        data = await analysis_repo.get_top_skills(db, top_number=top_number)
        return data
    except Exception as e:
        logger.error(f"error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str("Oops, sorry, our server went wrong"))
    
@analysis_router.get("/analysis/job-company-type", response_model=analysis.GetNumberOfCompanyTypeResponse)
async def get_number_of_company_type(db: Session = Depends(PostgresDB.get_db)):
    try:
        data = await analysis_repo.number_of_company_type(db)
        return data
    except Exception as e:
        logger.error(f"error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str("Oops, sorry, our server went wrong"))
    
@analysis_router.get("/analysis/new-user-in-time-range", response_model=analysis.GetNumberOfNewUser)
async def list_new_user_in_time_range(
    time_from: str = Query(None, description="Start time to calculate number of new users"),
    time_to: str = Query(None, description="End time to calculate number of new users"),
    db: Session = Depends(PostgresDB.get_db)
):
    try:
        data = await analysis_repo.get_number_of_new_user(db, time_from=time_from, time_to=time_to)
        return data
    except Exception as e:
        logger.error(f"error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str("Oops, sorry, our server went wrong"))
    
@analysis_router.get("/analysis/count-user-by-role", response_model=analysis.GetNumberOfAllNewUser)
async def count_new_user_by_role(
    db: Session = Depends(PostgresDB.get_db)
):
    try:
        data = await analysis_repo.count_all_number_of_user_by_role(db)
        return data
    except Exception as e:
        logger.error(f"error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str("Oops, sorry, our server went wrong"))
    
@analysis_router.get("/analysis/job-status", response_model=analysis.GetNumberOfJobStatus)
async def percentage_of_different_job_status(
    db: Session = Depends(PostgresDB.get_db)
):
    try:
        data = await analysis_repo.percentage_of_different_job_status(db)
        return data
    except Exception as e:
        logger.error(f"error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str("Oops, sorry, our server went wrong"))

@analysis_router.get("/analysis/top-recruiter-by-job-posting", response_model=analysis.GetTopRecruiterJobPosting)
async def get_top_recruiters_job_posting(
    top_number: int = Query(None, description="Top number of recruiter"),
    time_from: str = Query(None, description="Start time to find out the top recruiter"),
    time_to: str = Query(None, description="End time to find out the top recruiter"),
    db: Session = Depends(PostgresDB.get_db)
):
    try:
        data = await analysis_repo.get_top_recruiters_job_posting(db, top_number, time_from, time_to)
        return data
    except Exception as e:
        logger.error(f"error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str("Oops, sorry, our server went wrong"))
    
@analysis_router.get("/analysis/top-viewed-job", response_model=analysis.GetTopViewedJob)
async def get_top_viewed_jobs(
    top_number: int = Query(None, description="Top number of highest viewed jobs"),
    time_from: str = Query(None, description="Start time of time to get the viewed jobs"),
    time_to: str = Query(None, description="End time of time to get the viewed jobs"),
    db: Session = Depends(PostgresDB.get_db)
):
    try:
        data = await analysis_repo.get_top_viewed_jobs(db, top_number, time_from, time_to)
        return data
    except Exception as e:
        logger.error(f"error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str("Oops, sorry, our server went wrong"))

@analysis_router.get("/analysis/top-work-titles", response_model=analysis.ListTopWorkTitlesResponse)
async def list_top_work_titles(
    top_number: int = Query(None, description="Top number"),
    db: Session = Depends(PostgresDB.get_db)
):
    try:
        data = await analysis_repo.get_top_work_titles(db, top_number=top_number)
        return data
    except Exception as e:
        logger.error(f"error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str("Oops, sorry, our server went wrong"))
    
@analysis_router.get("/analysis/salary-change-by-time", response_model=analysis.ListChangeJobSalaryResponse)
async def get_change_of_job_salary_by_time(
    time_from: str = Query(None, description="Start month"),
    time_to: str = Query(None, description="End month"),
    level: str = Query(None, description="Hiring level"),
    db: Session = Depends(PostgresDB.get_db)
):
    try:        
        data = await analysis_repo.get_change_job_salary_by_time(db, time_from=time_from, time_to=time_to, level=level)
        return data
    except Exception as e:
        logger.error(f"error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str("Oops, sorry, our server went wrong"))
    
@analysis_router.get("/analysis/number-jobs-by-city", response_model=analysis.ListNumberofJobsByCityResponse)
async def get_number_of_job__by_city(
    country: str = Query(None, description="Country name"),
    job_title: str = Query(None, description="Common job title"),
    level: str = Query(None, description="Hiring level"),
    db: Session = Depends(PostgresDB.get_db)
):
    try:        
        data = await analysis_repo.get_number_jobs_by_city(db, job_title=job_title, country=country, level=level)
        return data
    except Exception as e:
        logger.error(f"error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str("Oops, sorry, our server went wrong"))