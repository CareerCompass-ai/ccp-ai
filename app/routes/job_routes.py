from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter, Query
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
def list_jobs_from_qdrant(
    page: Optional[int] = Query(None, description="Page number"),
    size: Optional[int] = Query(None, description="Page size"),
    input: Optional[str] = Query(None, description="Input text for vector search"),
    job_type: Optional[str] = Query(None, description="Job type filter"),
    company_type: Optional[str] = Query(None, description="Company type filter"),
    location: Optional[str] = Query(None, description="Location filter"),
    last_updated: Optional[str] = Query(None, description="Last updated filter"),
    salary_from: Optional[float] = Query(None, description="Minimum salary filter"),
    salary_to: Optional[float] = Query(None, description="Maximum salary filter"),
    hiring_level: Optional[list[str]] = Query(None, description="Hiring level filter"),
    applied_count: Optional[int] = Query(None, description="Applied count filter"),
    job_tags: Optional[list[str]] = Query(None, description="Job tags filter"),
    search_type: Optional[str] = Query(None, description="Search type: 'vector' or 'fulltext'")
):
    # map query params to req
    try:
        req = job.ListJobRequest(
            page=page,
            size=size,
            input=input,
            job_type=job_type,
            company_type=company_type,
            location=location,
            last_updated=last_updated,
            salary_from=salary_from,
            salary_to=salary_to,
            hiring_level=hiring_level,
            applied_count=applied_count,
            job_tags=job_tags,
            search_type=search_type
        )

        if search_type == "vector":
            if input is not None:
                vectors = ai_helper.get_embedding(input)
                req.vectors = vectors.tolist() if vectors is not None else None

            data = job_qdrant_repo.list_jobs(input=req)

            return data
        elif search_type == "fulltext":
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
    
# @job_router.get("/jobs", response_model=job.ListJobResponse)
# def list_jobs_from_qdrant(req: Optional[job.ListJobRequest]):
#     try:
#         if req.search_type == "vector":
#             if req.input is not None:
#                 vectors = ai_helper.get_embedding(req.input)
#                 req.vectors = vectors.tolist() if vectors is not None else None

#             data = job_qdrant_repo.list_jobs(input=req)

#             return data
#         elif req.search_type == "fulltext":
#             data = job_es_repo.list_jobs(input=req)

#             return data
#         else:
#             return job.ListJobResponse(
#                 count=0,
#                 page=req.size,
#                 size=req.size,
#                 records=list[job.JobAggregate]
#             )

#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))


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