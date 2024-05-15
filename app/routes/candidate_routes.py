from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter, Query
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

from app.repo.candidate_repo import CandidateRepository
from app.repo.resume_repo import ResumeRepository
from typing import Optional
from datetime import datetime
from app.dto import candidate
from app.dto import resume
from config.postgres import PostgresDB
from models.ccp_job_saved import JobSaved
from models.ccp_viewedjob import ViewedJob

from pkg.logging import logger

candidate_router = APIRouter(
    prefix="/api",
    tags=['Candidate']
)

candidate_repo = CandidateRepository()
resume_repo = ResumeRepository()

@candidate_router.get("/candidate/applied", response_model=candidate.ListAppliedJobsResponse)
def list_jobs_applied(
        candidate_id: Optional[int] = Query(None, description="Candidate/User ID"),
    ):
    try:
        data = candidate_repo.get_applied_jobs(candidate_id)
        return data
    except Exception as e:
        logger.error(f"error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str("Oops, sorry, our server went wrong"))
    
@candidate_router.post("/candidate/update-saved-job", response_model=candidate.UpdateSaveJobResponse)
def update_saved_job(
    req: candidate.UpdateSaveJobRequest
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
            candidate_repo.create_saved_job(record)
            return candidate.UpdateSaveJobResponse(
                message="Save job successfully!"
            )
        elif req.type == 2:
            candidate_repo.delete_saved_job(record)
            return candidate.UpdateSaveJobResponse(
                message="Unsave job sucessfully"
            ) 
    # except Exception as e:
    #     logger.error(f"error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str("Oops, sorry, our server went wrong"))
    except IntegrityError as e:
        # raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="You have already saved this job.")
        logger.error(f"error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str("Oops, sorry, our server went wrong"))
    
@candidate_router.get("/candidate/saved-jobs", response_model=candidate.ListSavedJobsResponse)
def list_jobs_saved(
    candidate_id: Optional[int] = Query(None, description="Candidate/User ID"),
):
    try: 
        data = candidate_repo.get_saved_jobs(candidate_id)
        return data
    except Exception as e:
        logger.error(f"error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str("Oops, sorry, our server went wrong"))

@candidate_router.get("/resumes", response_model=resume.GetResumesOfCandidateResponse)
async def list_resume_of_candidate(
    candidate_id: Optional[int] = Query(None, description="Candidate ID"),
):
    try:
        data = await resume_repo.get_by_user_id(candidate_id)

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
    except Exception as e:
        logger.error(f"error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str("Oops, sorry, our server went wrong"))