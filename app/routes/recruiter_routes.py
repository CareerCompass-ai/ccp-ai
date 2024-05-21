from fastapi import status, HTTPException, Depends, APIRouter, Query
import traceback
from datetime import datetime

from app.dto import recruiter

from models.ccp_talent_saved import TalentSaved

from app.repo.recruiter_repo import RecruiterRepository
from app.repo.talent_saved_repo import TalentSavedRepository

from pkg.logging import logger

recruiter_router = APIRouter(
    prefix="/api",
    tags=['Recruiter']
)

recruiter_repo = RecruiterRepository()
talent_repo = TalentSavedRepository()

@recruiter_router.get("/recruiter/jobs-posted", response_model=recruiter.ListJobsPostedResponse)
async def list_jobs_posted(
    recruiter_id: int = Query(None, description="recuiter ID"),
):
    try:
        data = await recruiter_repo.get_jobs_posted(recruiter_id)
        return data
    except Exception:
        logger.error(f"list_jobs_posted failed error = {traceback.format_exc()}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str("Oops, sorry, our server went wrong"))
    
@recruiter_router.post("/recruiter/update-saved-talent", response_model=recruiter.SaveTalentResponse)
async def update_saved_talent(
    req: recruiter.SaveTalentRequest
):
    try:
        now = datetime.now()
        record = TalentSaved(
            recruiter_id=req.recruiter_id,
            candidate_id=req.candidate_id,
            created_at=now,
            updated_at=now
        )

        if req.type == 1:
            await talent_repo.create_saved_talent(record)
            return recruiter.SaveTalentResponse (msg= "Save Talent Successfully!")
        
        elif req.type == 2:
            await talent_repo.delete_saved_talent(record)
            return recruiter.SaveTalentResponse (msg= "Unsave Talent Successfully!")
        
    
    except Exception:
        logger.error(f"update_saved_talent failed error = {traceback.format_exc()}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str("Oops, sorry, our server went wrong"))
    
@recruiter_router.get("/recruiter/candidates-saved", response_model=recruiter.ListTalentSavedResponse)
async def list_candidates_saved(
    recruiter_id: int = Query(None, description="recuiter ID"),
):
    try:
        data = await recruiter_repo.get_talents_saved(recruiter_id)
        return data
    except Exception:
        logger.error(f"list_candidates_saved failed error = {traceback.format_exc()}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str("Oops, sorry, our server went wrong"))