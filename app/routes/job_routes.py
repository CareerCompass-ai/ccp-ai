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
    prefix="/api",
    tags=['Job']
)

job_qdrant_repo = JobQdrantRepository(index_name=qdrant.QDRANT_INDEX_JOB_SEARCH)
job_repo = JobRepository()
ai_helper = AI()

@job_router.get("/jobs", response_model=job.ListJobResponse)
def list_jobs_from_qdrant(req: Optional[job.ListJobRequest]):
    try:
        if req.input is not None:
            vectors = ai_helper.get_embedding(req.input)
            req.vectors = vectors.tolist() if vectors is not None else None

        data = job_qdrant_repo.list_jobs(input=req)
        return data

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@job_router.get("/job", response_model=job.JobAggregate)
def get_job_from_qdrant(req: Optional[job.GetJobRequest]):
    try:
        data = job_qdrant_repo.get_job(input=req)
        return data

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

@job_router.get("/qdrant/health-check")
async def root():
    return {"message": "Good"}