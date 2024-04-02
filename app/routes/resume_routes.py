from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from typing import List, Optional
from sqlalchemy import func


from config.qdrant import QdrantVDB as qdrant
from config.es import ElasticSearchDB as es

from app.repo.resume_qdrant_repo import ResumeQdrantRepository
from app.repo.resume_minio_repo import ResumeMinioRepository
from app.repo.resume_repo import ResumeRepository
from app.dto import resume


resume_router = APIRouter(
    prefix="/api",
    tags=['Resume']
)

resume_qdrant_repo = ResumeQdrantRepository(index_name=qdrant.QDRANT_INDEX_RESUME_SEARCH)
resume_minio_repo = ResumeMinioRepository()
resume_repo = ResumeRepository()

# TODO: double check and remove this @ngoctrana
@resume_router.get("/resumes", response_model=resume.ListResumeResponse)
def list_resumes_from_qdrant(req: Optional[resume.ListResumeRequest]):
    try:
        data = resume_qdrant_repo.list_resumes(input=req)
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@resume_router.post("/resume/upload", response_model=resume.ResumeResponse_Url)
def upload_resume_to_minio(req: Optional[resume.ResumeurlRequest]):
    try:
        data = resume_minio_repo.upload_resume_to_minio(input=req)
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))  

@resume_router.post("/resume/create")
def post_resume(req: Optional[resume.ResumeRequest]):
    try:
        content = resume_minio_repo.convert_resume_to_content(input=req)
        req.content = content.content
        resume_repo.post_resume(input=req)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))      