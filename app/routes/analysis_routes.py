import traceback

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.dto import analysis
from app.factory.factory import RepositoryFactory as factory
from config.postgres import PostgresDB
from pkg.logging import logger

analysis_router = APIRouter(
    prefix="/api",
    tags=['Analysis']
)

analysis_repo = factory.get_analysis_repo()

#1
@analysis_router.get("/analysis/top-job-titles", response_model=analysis.ListTopJobTitlesResponse)
async def list_top_job_titles(
    top_number: int = Query(None, description="Top number of hiring jobs"),
    time_from: str = Query(None, description="Start time of time to get the top hiring jobs"),
    time_to: str = Query(None, description="End time of time to get the top hiring jobs"),
    db: Session = Depends(PostgresDB.get_db)
):
    try:
        data = await analysis_repo.get_top_job_titles(db=db, top_number=top_number, time_from=time_from, time_to=time_to)
        return data
    except Exception:
        logger.error(f"list_top_job_titles failed error = {traceback.format_exc()}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str("Oops, sorry, our server went wrong"))
    
#5
@analysis_router.get("/analysis/top-job-titles-salary", response_model=analysis.ListTopJobTitlesSalaryResponse)
async def list_top_job_titles_salary(
    top: int = Query(None, description="Number of records"),
    country_name: str = Query(None, description="Selected country name"),
    time: str = Query(None, description="Selected time range (month or year)"),
    time_from: str = Query(None, description="Time range from"),
    time_to: str = Query(None, description="Time range to"),
    order_by: int = Query(None, description="1: desc and 0: asc"),
    db: Session = Depends(PostgresDB.get_db)
):
    try:
        data = await analysis_repo.get_top_leader_salaries(db=db, country_name= country_name, time=time, time_from=time_from, time_to=time_to, limit=top, order=order_by)
        return data
    except Exception:
        logger.error(f"list_top_job_titles_salary failed error = {traceback.format_exc()}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str("Oops, sorry, our server went wrong"))
    
#6
@analysis_router.get("/analysis/top-applied-job-titles", response_model=analysis.ListTopAppliedJobTitlesResponse)
async def list_top_applied_job_titles(
    top_number: int = Query(None, description="Number of records"),
    time_from: str = Query(None, description="Start time of time to get top apply job"),
    time_to: str = Query(None, description="End time of time to get top apply job"),
    db: Session = Depends(PostgresDB.get_db)
):
    try:
        data = await analysis_repo.get_most_applied_job_titles(db=db, top_number=top_number,time_from=time_from, time_to=time_to)
        return data
    except Exception:
        logger.error(f"list_top_applied_job_titles failed error = {traceback.format_exc()}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str("Oops, sorry, our server went wrong"))
    
@analysis_router.get("/analysis/top-skills", response_model=analysis.GetTopSkillResponse)
async def list_top_skills(
    top_number: int = Query(None, description="Top number of skills"),
    time: str = Query(None, description="Selected time range"),
    db: Session = Depends(PostgresDB.get_db)
):
    try:
        data = await analysis_repo.get_top_skills(db=db, top_number=top_number, time=time)
        return data
    except Exception:
        logger.error(f"list_top_skills failed error = {traceback.format_exc()}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str("Oops, sorry, our server went wrong"))
    
@analysis_router.get("/analysis/job-company-type", response_model=analysis.GetNumberOfCompanyTypeResponse)
async def get_number_of_company_type(db: Session = Depends(PostgresDB.get_db)):
    try:
        data = await analysis_repo.number_of_company_type(db=db)
        return data
    except Exception:
        logger.error(f"get_number_of_company_type failed error = {traceback.format_exc()}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str("Oops, sorry, our server went wrong"))
    
@analysis_router.get("/analysis/new-user-in-time-range", response_model=analysis.GetNumberOfNewUser)
async def list_new_user_in_time_range(
    time: str = Query(None, description="Time range (Month/year)"),
    time_from: str = Query(None, description="Start time to calculate number of new users"),
    time_to: str = Query(None, description="End time to calculate number of new users"),
    db: Session = Depends(PostgresDB.get_db)
):
    try:
        data = await analysis_repo.get_number_of_new_user(db=db, time=time, time_from=time_from, time_to=time_to)
        return data
    except Exception:
        logger.error(f"list_new_user_in_time_range failed error = {traceback.format_exc()}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str("Oops, sorry, our server went wrong"))
    
@analysis_router.get("/analysis/count-user-by-role", response_model=analysis.GetNumberOfAllNewUser)
async def count_new_user_by_role(
    db: Session = Depends(PostgresDB.get_db)
):
    try:
        data = await analysis_repo.count_all_number_of_user_by_role(db=db)
        return data
    except Exception:
        logger.error(f"count_new_user_by_role failed error = {traceback.format_exc()}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str("Oops, sorry, our server went wrong"))
    
@analysis_router.get("/analysis/job-status", response_model=analysis.GetNumberOfJobStatus)
async def percentage_of_different_job_status(
    db: Session = Depends(PostgresDB.get_db)
):
    try:
        data = await analysis_repo.percentage_of_different_job_status(db=db)
        return data
    except Exception:
        logger.error(f"percentage_of_different_job_status failed error = {traceback.format_exc()}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str("Oops, sorry, our server went wrong"))

@analysis_router.get("/analysis/top-recruiter-by-job-posting", response_model=analysis.GetTopRecruiterJobPosting)
async def get_top_recruiters_job_posting(
    top_number: int = Query(None, description="Top number of recruiter"),
    time: str = Query(None, description="Selected time range"),
    time_from: str = Query(None, description="Start time to find out the top recruiter"),
    time_to: str = Query(None, description="End time to find out the top recruiter"),
    db: Session = Depends(PostgresDB.get_db)
):
    try:
        data = await analysis_repo.get_top_recruiters_job_posting(db=db, top_number=top_number, time=time, time_from=time_from, time_to=time_to)
        return data
    except Exception:
        logger.error(f"get_top_recruiters_job_posting failed error = {traceback.format_exc()}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str("Oops, sorry, our server went wrong"))
    
@analysis_router.get("/analysis/top-viewed-job", response_model=analysis.GetTopViewedJob)
async def get_top_viewed_jobs(
    top_number: int = Query(None, description="Top number of highest viewed jobs"),
    time_from: str = Query(None, description="Start time of time to get the viewed jobs"),
    time_to: str = Query(None, description="End time of time to get the viewed jobs"),
    db: Session = Depends(PostgresDB.get_db)
):
    try:
        data = await analysis_repo.get_top_viewed_jobs(db=db, top_number=top_number, time_from=time_from, time_to=time_to)
        return data
    except Exception:
        logger.error(f"get_top_viewed_jobs failed error = {traceback.format_exc()}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str("Oops, sorry, our server went wrong"))

@analysis_router.get("/analysis/top-work-titles", response_model=analysis.ListTopWorkTitlesResponse)
async def list_top_work_titles(
    top_number: int = Query(None, description="Top number"),
    db: Session = Depends(PostgresDB.get_db)
):
    try:
        data = await analysis_repo.get_top_work_titles(db=db, top_number=top_number)
        return data
    except Exception:
        logger.error(f"list_top_work_titles failed error = {traceback.format_exc()}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str("Oops, sorry, our server went wrong"))
    
@analysis_router.get("/analysis/salary-change-by-time", response_model=analysis.ListChangeJobSalaryResponse)
async def get_change_of_job_salary_by_time(
    time_from: str = Query(None, description="Start month"),
    time_to: str = Query(None, description="End month"),
    level: str = Query(None, description="Hiring level"),
    db: Session = Depends(PostgresDB.get_db)
):
    try:        
        data = await analysis_repo.get_change_job_salary_by_time(db=db, time_from=time_from, time_to=time_to, level=level)
        return data
    except Exception:
        logger.error(f"get_change_of_job_salary_by_time failed error = {traceback.format_exc()}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str("Oops, sorry, our server went wrong"))
    
@analysis_router.get("/analysis/salary-change-by-year", response_model=analysis.ListChangeJobSalaryByYearResponse)
async def get_change_of_job_salary_by_year(
    job_title: str = Query(None, description="Selected job title"),
    time: str = Query(None, description="Time range"),
    time_from: str = Query(None, description="Time range from"),
    time_to: str = Query(None, description="Time range to"),
    country_name: str = Query(None, description="Selected country"),
    db: Session = Depends(PostgresDB.get_db)
):
    try:        
        data = await analysis_repo.get_change_job_salary_by_year(db=db, time=time, time_from=time_from, time_to=time_to, country_name=country_name, job_title=job_title)
        return data
    except Exception:
        logger.error(f"get_change_of_job_salary_by_time failed error = {traceback.format_exc()}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str("Oops, sorry, our server went wrong"))
    
@analysis_router.get("/analysis/number-jobs-by-country", response_model=analysis.ListNumberofJobsByCountryResponse)
async def get_number_jobs_by_country(
    country_name: str = Query(None, description="Country name"),
    time: str = Query(None, description="Time range"),
    time_from: str = Query(None, description="Time range from"),
    time_to: str = Query(None, description="Time range to"),
    job_title: str = Query(None, description="Common job title"),
    level: str = Query(None, description="Hiring level"),
    db: Session = Depends(PostgresDB.get_db)
):
    try:        
        data = await analysis_repo.get_number_jobs_by_country(db=db, job_title=job_title, country_name=country_name, time=time, time_from= time_from, time_to = time_to, level=level)
        return data
    except Exception:
        logger.error(f"get_number_of_job__by_country failed error = {traceback.format_exc()}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str("Oops, sorry, our server went wrong"))
    
@analysis_router.get("/analysis/get-countries", response_model=analysis.ListCountryName)
async def get_country(
    db: Session = Depends(PostgresDB.get_db)
):
    try:        
        data = await analysis_repo.get_list_country(db=db)
        return data
    except Exception:
        logger.error(f"get_number_of_job__by_city failed error = {traceback.format_exc()}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str("Oops, sorry, our server went wrong"))
    
@analysis_router.get("/analysis/get-common-job-titles", response_model=analysis.ListJobTitle)
async def get_common_job_titles(
    db: Session = Depends(PostgresDB.get_db)
):
    try:        
        data = await analysis_repo.get_list_common_job_title(db=db)
        return data
    except Exception:
        logger.error(f"get_number_of_job__by_city failed error = {traceback.format_exc()}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str("Oops, sorry, our server went wrong"))