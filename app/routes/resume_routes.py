from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from typing import List, Optional
from sqlalchemy import func

from config.postgres import PostgresDB
from config.qdrant import QdrantVDB as qdrant
from config.es import ElasticSearchDB as es

from app.repo.job_es_repo import JobESRepository
from app.repo.resume_qdrant_repo import ResumeQdrantRepository
from app.repo.job_repo import JobRepository 
from app.repo.resume_minio_repo import ResumeMinioRepository
from app.dto import resume

from app.ai.ai_helper import AI
from minio import Minio

resume_router = APIRouter(
    prefix="/api",
    tags=['Resume']
)

resume_qdrant_repo = ResumeQdrantRepository(index_name=qdrant.QDRANT_INDEX_RESUME_SEARCH)
resume_minio_repo = ResumeMinioRepository()
job_repo = JobRepository()
ai_helper = AI()

# TODO: double check and remove this @ngoctrana
@resume_router.get("/resumes", response_model=resume.ListResumeResponse)
def list_resumes_from_qdrant(req: Optional[resume.ListResumeRequest]):
    try:
        data = resume_qdrant_repo.list_resumes(input=req)
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@resume_router.post("/upload/resume", response_model=resume.ResumeResponse_Url)
def upload_resume_to_minio(req: Optional[resume.ResumeurlRequest]):
    try:
        data = resume_minio_repo.upload_resume_to_minio(input=req)
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))  
