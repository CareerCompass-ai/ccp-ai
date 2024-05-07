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
#1
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
    
#5
@analysis_router.get("/analysis/top-job-titles-salary", response_model=List[analysis.GetTopJobTitlesSalaryResponse])
def list_top_job_titles_salary(
    top: int = Query(None, description="Number of records"),
    level: str = Query(None, description="Hiring Level"),
    order_by: int = Query(None, description="1: desc and 2: asc")
):
    try:
        data = analysis_repo.get_top_leader_salaries(limit=top, hiring_level=level, order=order_by)
        return data
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))