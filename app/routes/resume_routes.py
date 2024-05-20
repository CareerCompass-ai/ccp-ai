from fastapi import status, HTTPException, Depends, APIRouter, Query, Path, UploadFile, File, Form
from sqlalchemy import func
from datetime import datetime
import os, PyPDF2
import uuid
from io import BytesIO
import traceback

from config.qdrant import QdrantVDB as qdrant

from app.repo.resume_qdrant_repo import ResumeQdrantRepository
from app.repo.resume_minio_repo import ResumeMinioRepository
from app.repo.resume_repo import ResumeRepository
from app.dto import resume

from pkg.logging import logger

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

        # Generate file name
        file_name = str(uuid.uuid4()) + "_" + file.filename

        upload_response = resume_minio_repo.upload_resume_to_minio(
            resume.UploadResumeMinioRequest(temp_path=temp_file_path, file_name=file_name)
        )
        public_url = upload_response.url


        now = datetime.now()

        record = resume.ResumeBase(
            candidate_id=candidate_id,
            resume_name=file_name,
            resume_link=public_url,
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
        logger.error(f"create_resume failed error = {traceback.format_exc()}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str("Oops, sorry, our server went wrong"))
    finally:
        if file is not None:
            file.file.close()

@resume_router.put("/resume/delete", response_model=resume.DeleteResumeResponse)
async def delete(
    resume_id: int = Form(None),
):
    try:
        await resume_repo.delete_resume(resume_id)
        #Delete resume in MinIO or not?
        
        return resume.DeleteResumeResponse(msg="Delete resume successfully!")

    except Exception:
        logger.error(f"delete_resume failed error = {traceback.format_exc()}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str("Oops, sorry, our server went wrong"))
