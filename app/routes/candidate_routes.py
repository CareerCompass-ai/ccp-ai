import traceback
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.dto import candidate, resume
from app.repo.candidate_repo import CandidateRepository
from app.repo.resume_repo import ResumeRepository
from config.postgres import PostgresDB
from models.ccp_job_saved import JobSaved
from pkg.logging import logger

candidate_router = APIRouter(
    prefix="/api",
    tags=['Candidate']
)

candidate_repo = CandidateRepository()
resume_repo = ResumeRepository()

@candidate_router.get("/candidate/applied", response_model=candidate.ListAppliedJobsResponse)
async def list_jobs_applied(
        candidate_id: Optional[int] = Query(None, description="Candidate/User ID"),
        db: Session = Depends(PostgresDB.get_db)
    ):
    try:
        data = await candidate_repo.get_applied_jobs(db=db, id=candidate_id)
        return data
    except Exception:
        logger.error(f"list_jobs_applied failed error = {traceback.format_exc()}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str("Oops, sorry, our server went wrong"))
    
@candidate_router.post("/candidate/update-saved-job", response_model=candidate.UpdateSaveJobResponse)
async def update_saved_job(
    req: candidate.UpdateSaveJobRequest,
    db: Session = Depends(PostgresDB.get_db)
):
    try:
        now = datetime.now()
        record = JobSaved(
            candidate_id=req.candidate_id,
            job_id=req.job_id,
            created_at=now,
            updated_at=now,
        )

        if req.type == 1:
            await candidate_repo.create_saved_job(db=db, record=record)
            return candidate.UpdateSaveJobResponse(
                message="Save job successfully!"
            )
        elif req.type == 2:
            await candidate_repo.delete_saved_job(db=db, record=record)
            return candidate.UpdateSaveJobResponse(
                message="Unsave job sucessfully"
            ) 

    except Exception:
        # raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="You have already saved this job.")
        logger.error(f"update_saved_job failed error = {traceback.format_exc()}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str("Oops, sorry, our server went wrong"))
    
@candidate_router.get("/candidate/saved-jobs", response_model=candidate.ListSavedJobsResponse)
async def list_jobs_saved(
    candidate_id: Optional[int] = Query(None, description="Candidate/User ID"),
    db: Session = Depends(PostgresDB.get_db)
):
    try: 
        data = await candidate_repo.get_saved_jobs(db=db, id=candidate_id)
        return data
    except Exception:
        logger.error(f"list_jobs_saved failed error = {traceback.format_exc()}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str("Oops, sorry, our server went wrong"))

@candidate_router.get("/resumes", response_model=resume.GetResumesOfCandidateResponse)
async def list_resume_of_candidate(
    candidate_id: Optional[int] = Query(None, description="Candidate ID"),
    db: Session = Depends(PostgresDB.get_db)
):
    try:
        data = await resume_repo.get_by_user_id(db=db, user_id=candidate_id)

        resume_records = [resume.ResumeBase(
            id=res.id,
            candidate_id=res.candidate_id,
            # content=res.content,
            resume_link=res.resume_link,
            resume_name=res.resume_name,
            created_at=res.created_at,
            updated_at=res.updated_at
        ) for res in data]

        return resume.GetResumesOfCandidateResponse(records=resume_records)
    except Exception:
        logger.error(f"list_resume_of_candidate failed error = {traceback.format_exc()}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str("Oops, sorry, our server went wrong"))