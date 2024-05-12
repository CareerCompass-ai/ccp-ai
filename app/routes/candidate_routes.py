from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter, Query
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

from app.repo.candidate_repo import CandidateRepository
from typing import Optional
from datetime import datetime
from app.dto import candidate
from models.ccp_job_saved import JobSaved
from models.ccp_viewedjob import ViewedJob

candidate_router = APIRouter(
    prefix="/api",
    tags=['Candidate']
)

candidate_repo = CandidateRepository()

@candidate_router.get("/candidate/applied", response_model=candidate.ListAppliedJobsResponse)
def list_jobs_applied(
        candidate_id: Optional[int] = Query(None, description="Candidate/User ID"),
    ):
    try:
        data = candidate_repo.get_applied_jobs(candidate_id)
        return data
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    
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
    #     raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    except IntegrityError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="You have already saved this job.")
    
@candidate_router.get("/candidate/saved-jobs", response_model=candidate.ListSavedJobsResponse)
def list_jobs_saved(
    candidate_id: Optional[int] = Query(None, description="Candidate/User ID"),
):
    try: 
        data = candidate_repo.get_saved_jobs(candidate_id)
        return data
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    
@candidate_router.post("/candidate/view-job", response_model=candidate.JobViewdResponse)
def view_job(
    req: candidate.CreateJobViewedRequest
):
    try:    
        check = candidate_repo.check_viewed_job(candidate_id=req.candidate_id, job_id=req.job_id)
        if check is not None:
            return candidate.JobViewdResponse (
                message="You have seen this job",
                job_id=check.job_id,
                candidate_id=check.candidate_id,
                time=check.time
            )
        else:
            now = datetime.now()
            record = ViewedJob(
                candidate_id = req.candidate_id,
                job_id = req.job_id,
                view_datetime = now,
                created_at = now,
                updated_at = now
            )
            candidate_repo.create_viewd_job(record=record)
            return candidate.JobViewdResponse (
                message="View job sucessfully!",
                job_id=record.job_id,
                candidate_id=record.candidate_id,
                time=record.view_datetime
            )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))