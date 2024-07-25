import os
import traceback
from typing import Optional
import uuid
from datetime import datetime
from io import BytesIO

import PyPDF2
from xhtml2pdf import pisa
from better_profanity import profanity
from fastapi import (APIRouter, Depends, File, Form, HTTPException, UploadFile,
                     status)
from fastapi.templating import Jinja2Templates
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
        self.router.add_api_route("/resume/generate", self.generate, methods=["POST"], response_model=resume.GenerateResumeResponse)

        self.templates = Jinja2Templates(directory="app/templates")

    async def generate(
        self,
        req: Optional[resume.GenerateResumeRequest] = None, 
    ):
        temp_file_path = None  # Initialize temp_file_path
        try:
            # Generate template name and load template
            template_name = "resume_template_" + str(req.template) + ".html"
            template = self.templates.get_template(template_name)
            
            # Render HTML content
            html_content = template.render(
                user_name=req.payload.user_name,
                email=req.payload.email,
                portfolio=req.payload.portfolio,
                mobile=req.payload.mobile,
                github=req.payload.github,
                education_institution=req.payload.education_institution,
                education_details=req.payload.education_details,
                skills_summary=req.payload.skills_summary,
                work_experience=req.payload.work_experience,
                projects=req.payload.projects,
                publications=req.payload.publications or [],
                honors_and_awards=req.payload.honors_and_awards or [],
                volunteer_experience=req.payload.volunteer_experience or [],
                summary=req.payload.summary,
            )

            # Generate file name
            file_name = str(uuid.uuid4()) + "_" + req.resume_name + ".pdf"

            # Define URL before uploading to MinIO
            public_url = f"{minio_constant.SERVER_DOMAIN}/minio/{minio_constant.MINIO_BUCKET_RESUME}/{file_name}"
            download_url = "https://" + public_url
            pdf_file_path = file_name + ".pdf"

            # Create PDF and save to a temporary file
            result = BytesIO()
            pisa.CreatePDF(BytesIO(html_content.encode('utf-8')), dest=result)

            temp_dir = os.path.dirname(os.path.abspath(__file__))
            temp_file_path = os.path.join(temp_dir, pdf_file_path)

            with open(temp_file_path, 'wb') as f:
                f.write(result.getvalue())

            # Upload to MinIO
            await self.minio_repo.upload(
                minio.UploadMinioRequest(
                    bucket_name=minio_constant.MINIO_BUCKET_RESUME,
                    temp_path=temp_file_path,
                    file_name=file_name
                )
            )

            return resume.GenerateResumeResponse(status="Generate successfully!", download_url=download_url)
        except Exception:
            logger.error(f"generate_resume failed error = {traceback.format_exc()}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Oops, sorry, our server went wrong")
        finally:
            if temp_file_path and os.path.exists(temp_file_path):
                os.remove(temp_file_path)


    async def upload(
        self,
        candidate_id: str = Form(None),
        file: UploadFile = File(None),
        db: Session = Depends(PostgresDB.get_db)
    ):
        try:
            file_content = await file.read()

            # Check profanity in file name
            if profanity.contains_profanity(file.filename):
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Content contains profanity and cannot be accepted.")

            # Generate file name
            file_name = str(uuid.uuid4()) + "_" + file.filename

            # Define URL before uploading to MinIO
            public_url = f"{minio_constant.SERVER_DOMAIN}/minio/{minio_constant.MINIO_BUCKET_RESUME}/{file_name}"

            now = datetime.now()

            # Create a record
            record = resume.ResumeBase(
                candidate_id=candidate_id,
                resume_name=file_name,
                resume_link=public_url,
                created_at=now,
                updated_at=now
            )

            # Step 1: Save file temporarily
            temp_dir = os.path.dirname(os.path.abspath(__file__))
            temp_file_path = os.path.join(temp_dir, file.filename)
            with open(temp_file_path, "wb") as temp_file:
                temp_file.write(file_content)

            if file is not None:
                pdf_file = BytesIO(file_content)
                pdf_reader = PyPDF2.PdfReader(pdf_file)

                text_content = ""
                for page_num in range(len(pdf_reader.pages)):
                    text = pdf_reader.pages[page_num].extract_text()
                    text = text.replace('\x00', '').replace('\n', '').replace('\r', '').replace('\t', '').replace('\x1b', '')
                    text_content += text

                # Check profanity in content
                if profanity.contains_profanity(text_content):
                    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Content contains profanity and cannot be accepted.")

                record.content = text_content

            # Start transaction
            with db.begin():
                try:
                    # Step 2: Insert record into database
                    await self.resume_repo.post_resume(db=db, input=record)

                    # Step 3: Perform upload to MinIO
                    await self.minio_repo.upload(
                        minio.UploadMinioRequest(
                            bucket_name=minio_constant.MINIO_BUCKET_RESUME,
                            temp_path=temp_file_path,
                            file_name=file_name
                        )
                    )

                    os.remove(temp_file_path)

                except Exception as e:
                    # Rollback database transaction on any error
                    db.rollback()
                    logger.error(f"create_resume transaction failed error = {traceback.format_exc()}")
                    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Oops, sorry, our server went wrong")

            return resume.CreateResumePostResponse(message="Upload successfully!")
        
        except HTTPException:
            raise  # Let HTTPExceptions propagate as they are already handled
        except Exception:
            logger.error(f"create_resume failed error = {traceback.format_exc()}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Oops, sorry, our server went wrong")
        finally:
            if file is not None:
                file.file.close()
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)

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
