from typing import List, Optional
from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter, Query, Path, UploadFile, File, Form
from sqlalchemy import func
from sqlalchemy.orm import Session

from datetime import datetime
import os, PyPDF2
from io import BytesIO

from config.qdrant import QdrantVDB as qdrant
from config.postgres import PostgresDB

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

@resume_router.post("/resume/create", response_model=resume.CreateResumePostResponse)
async def upload(
    candidate_id: str = Form(None),
    file: UploadFile = File(None),
):
    try:
        file_content = await file.read()

        temp_dir = os.path.dirname(os.path.abspath(__file__))
        temp_file_path = os.path.join(temp_dir, file.filename)
        with open(temp_file_path, "wb") as temp_file:
            temp_file.write(file_content)
        
        url = resume_minio_repo.upload_resume_to_minio(input=resume.UploadResumeMinioRequest(temp_path=temp_file_path, file_name=file.filename))

        os.remove(temp_file_path)

        content_url = url.url

        now = datetime.now()

        record = resume.ResumeBase(
            candidate_id=candidate_id,
            resume_name=file.filename,
            resume_link=content_url,
            created_at=now,
            updated_at=now
        )

        if file is not None:

            pdf_file = BytesIO(file_content)

            pdf_reader = PyPDF2.PdfReader(pdf_file)

            text_content = ""
            for page_num in range(len(pdf_reader.pages)):
                text_content += pdf_reader.pages[page_num].extract_text()

            record.content = text_content

        await resume_repo.post_resume(input=record)

        return resume.CreateResumePostResponse
    except Exception:
        return {"message": "There was an error uploading or processing the PDF file"}

    finally:
        if file is not None:
            file.file.close()


@resume_router.get("/resumes", response_model=resume.GetResumesOfCandidateResponse)
async def list_resume_of_candidate(
    user_id: Optional[int] = Query(None, description="User ID"),
):
    try:
        data = await resume_repo.get_by_user_id(user_id)

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
    except Exception:
        return {"message": "There was an error listing resumes of a candidate"}