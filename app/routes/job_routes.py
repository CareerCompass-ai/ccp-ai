from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from typing import List, Optional
from sqlalchemy import func

from config.postgres import PostgresDB
from config.qdrant import QdrantVDB as qdrant

from app.repo.job_qdrant_repo import JobQdrantRepository
from app.repo.job_repo import JobRepository 

from app.dto import job

from app.ai.ai_helper import AI

job_router = APIRouter(
    prefix="/api/job",
    tags=['Job']
)

job_qdrant_repo = JobQdrantRepository(index_name=qdrant.QDRANT_INDEX_JOB_SEARCH)
job_repo = JobRepository()
ai_helper = AI()

@job_router.get("/list", response_model=List[job.ListJobResponse])
def list_jobs_from_qdrant(req: Optional[job.ListJobRequest]):
    print("ListJobRequest: ", req)

    if req.input is not None:
        vectors = ai_helper.get_embedding(req.input)

        req.vectors=vectors

    job_ids = job_qdrant_repo.list_jobs(input=req)
    return job_ids

# api for test
@job_router.get("/list-pg", response_model=job.ListJobResponse)
def get_jobs(request: job.ListJobRequest, db: Session = Depends(PostgresDB.get_db)):
    print("ListJobRequest: ", request)

    jobs = job_repo.get_jobs(db)
    job_responses = [job.JobAggregate(**j.__dict__) for j in jobs]

    response = job.ListJobResponse(
        count=len(job_responses),
        page=request.page,
        size=request.size,
        records=job_responses
    )

    return response

@job_router.get("/", response_model=List[job.JobBase])
def get_jobs(id: int, db: Session =  Depends(PostgresDB.get_db)):
    job = job_repo.get_by_id(db, id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    return job

@job_router.get("/qdrant/health-check")
async def root():
    return {"message": "Good"}