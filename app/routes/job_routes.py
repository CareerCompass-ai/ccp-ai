from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from typing import List, Optional
from sqlalchemy import func

from config.postgres import PostgresDB
from config.qdrant import QdrantVDB as qdrant
from config.es import ElasticSearchDB as es

from app.repo.job_es_repo import JobESRepository
from app.repo.job_qdrant_repo import JobQdrantRepository
from app.repo.job_repo import JobRepository 

from app.dto import job

from app.ai.ai_helper import AI

job_router = APIRouter(
    prefix="/api",
    tags=['Job']
)
job_es_repo = JobESRepository(index_name=es.ES_INDEX_JOB_SEARCH)
job_qdrant_repo = JobQdrantRepository(index_name=qdrant.QDRANT_INDEX_JOB_SEARCH)
job_repo = JobRepository()
ai_helper = AI()

@job_router.get("/jobs", response_model=job.ListJobResponse)
def list_jobs_from_qdrant(req: Optional[job.ListJobRequest]):
    try:
        if req.search_type == "vector":
            if req.input is not None:
                vectors = ai_helper.get_embedding(req.input)
                req.vectors = vectors.tolist() if vectors is not None else None

            data = job_qdrant_repo.list_jobs(input=req)

            return data
        elif req.search_type == "fulltext":
            data = job_es_repo.list_jobs(input=req)

            return data
        else:
            return job.ListJobResponse(
                count=0,
                page=req.size,
                size=req.size,
                records=list[job.JobAggregate]
            )

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