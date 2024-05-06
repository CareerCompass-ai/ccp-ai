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