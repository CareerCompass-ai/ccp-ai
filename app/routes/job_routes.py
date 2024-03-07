from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from typing import List, Optional
from sqlalchemy import func

from config import postgres
from models import ccp_job
from app.dto import job

from app.repo import job_repo 

job_router = APIRouter(
    prefix="/api/job",
    tags=['Job']
)

@job_router.get("/list", response_model=List[job.ListJobResponse])
def get_jobs(db: Session = Depends(postgres.init_db)):
    jobs = job_repo.JobRepository.get_jobs(db)
    return [job.ListJobResponse(**j.__dict__) for j in jobs]

@job_router.get("/", response_model=List[job.JobBase])
def get_jobs(id: int, db: Session = Depends(postgres.init_db)):
    job = job_repo.JobRepository.get_by_id(db, id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


@job_router.get("/ping")
async def root():
    return {"message": "pong"}