import os
import traceback
import uuid
from datetime import datetime
from io import BytesIO

import PyPDF2
from fastapi import (APIRouter, Depends, File, Form, HTTPException, UploadFile,
                     status)
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

import constant.config as minio_constant
from app.dto import minio, resume
from app.factory.factory import RepositoryFactory as factory
from config.postgres import PostgresDB
from pkg.logging import logger


class ResumeRouter:
    def __init__(self):
        self.resume_qdrant_repo = factory.get_resume_qdrant_repo()
        self.resume_repo = factory.get_resume_repo()
        self.minio_repo = factory.get_minio_repo()
        self.router = APIRouter(prefix="/api", tags=['Resume'])
        self.router.add_api_route("/resume/create", self.upload, methods=["POST"], response_model=resume.CreateResumePostResponse)
        self.router.add_api_route("/resume/delete", self.delete, methods=["PUT"], response_model=resume.DeleteResumeResponse)

    async def upload(
        self,
        candidate_id: str = Form(None),
        file: UploadFile = File(None),
        db: Session = Depends(PostgresDB.get_db)
    ):
        try:
            file_content = await file.read()

            temp_dir = os.path.dirname(os.path.abspath(__file__))
            temp_file_path = os.path.join(temp_dir, file.filename)
            with open(temp_file_path, "wb") as temp_file:
                temp_file.write(file_content)

            # Generate file name
            file_name = str(uuid.uuid4()) + "_" + file.filename

            upload_response = await self.minio_repo.upload(
                minio.UploadMinioRequest(bucket_name=minio_constant.MINIO_BUCKET_RESUME, temp_path=temp_file_path, file_name=file_name)
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
                    text = pdf_reader.pages[page_num].extract_text()
                    text = text.replace('\x00', '').replace('\n', '').replace('\r', '').replace('\t', '').replace('\x1b', '')
                    text_content += text

                record.content = text_content

            os.remove(temp_file_path)

            with db.begin():
                try:
                    await self.resume_repo.post_resume(db=db, input=record)
                    return resume.CreateResumePostResponse
                except SQLAlchemyError:
                    db.rollback()
                    logger.error(f"create_resume failed error = {traceback.format_exc()}")
                    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str("Oops, sorry, our server went wrong"))
        except Exception:
            logger.error(f"create_resume failed error = {traceback.format_exc()}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str("Oops, sorry, our server went wrong"))
        finally:
            if file is not None:
                file.file.close()

    async def delete(
        self,
        req: resume.DeleteResumeRequest,
        db: Session = Depends(PostgresDB.get_db)
    ):
        try:
            now = datetime.now()

            props = {
                "active": False,
                'updated_at': now,
            }

            await self.resume_repo.update_with_map(db=db, resume_id=req.resume_id, props=props)
            
            #Delete resume in MinIO or not?
            
            return resume.DeleteResumeResponse(msg="Delete resume successfully!")

        except Exception:
            logger.error(f"delete_resume failed error = {traceback.format_exc()}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str("Oops, sorry, our server went wrong"))


resume_router = ResumeRouter().router
