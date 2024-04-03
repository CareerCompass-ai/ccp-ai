from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter, Query, Path, UploadFile, File, Form
from sqlalchemy import func
from config.qdrant import QdrantVDB as qdrant

from app.repo.resume_qdrant_repo import ResumeQdrantRepository
from app.repo.resume_minio_repo import ResumeMinioRepository
from app.repo.resume_repo import ResumeRepository
from app.dto import resume

import os, PyPDF2
from io import BytesIO

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
        content = await file.read()

        temp_dir = os.path.dirname(os.path.abspath(__file__))
        temp_file_path = os.path.join(temp_dir, file.filename)
        with open(temp_file_path, "wb") as temp_file:
            temp_file.write(content)
        
        url = resume_minio_repo.upload_resume_to_minio(input=resume.UploadResumeMinioRequest(temp_path=temp_file_path, file_name=file.filename))

        os.remove(temp_file_path)

        content_url = url.url

        record = resume.ResumeBase(
            candidate_id=candidate_id,
            resume_name=file.filename,
            resume_link=content_url,
        )

        if file is not None:

            pdf_file = BytesIO(content)

            pdf_reader = PyPDF2.PdfReader(pdf_file)

            text_content = ""
            for page_num in range(len(pdf_reader.pages)):
                text_content += pdf_reader.pages[page_num].extract_text()

            record.content = text_content

        resume_repo.post_resume(input=record)

        return resume.CreateResumePostResponse
    except Exception:
        return {"message": "There was an error uploading or processing the PDF file"}

    finally:
        if file is not None:
            file.file.close()