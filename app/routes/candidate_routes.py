from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter, Query
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

from app.repo.candidate_repo import CandidateRepository
from typing import Optional

from app.dto import candidate

candidate_router = APIRouter(
    prefix="/api",
    tags=['Candidate']
)

candidate_repo = CandidateRepository()

@candidate_router.get("/candidate/applied", response_model=candidate.ListAppliedJobsResponse)
def list_jobs_applied(
        id: Optional[int] = Query(None, description="Candidate/User ID"),
    ):
    try:
        data = candidate_repo.get_applied_jobs(id)
        return data
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))