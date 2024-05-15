from fastapi import status, HTTPException, Depends, APIRouter, Query

from app.dto import recruiter

from app.repo.recruiter_repo import RecruiterRepository

import constant.common as constant

from pkg.logging import logger

recruiter_router = APIRouter(
    prefix="/api",
    tags=['Recruiter']
)

recruiter_repo = RecruiterRepository()

@recruiter_router.get("/recruiter/jobs-posted", response_model=recruiter.ListJobsPostedResponse)
async def list_jobs_posted(
    recruiter_id: int = Query(None, description="recuiter ID"),
):
    try:
        data = await recruiter_repo.get_jobs_posted(recruiter_id)
        return data
    except Exception as e:
        logger.error(f"error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str("Oops, sorry, our server went wrong"))