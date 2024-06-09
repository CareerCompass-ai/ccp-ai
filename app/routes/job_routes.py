import os
import traceback
import uuid
from datetime import datetime
from io import BytesIO
from typing import Optional
import re

import fitz
import pymupdf4llm
import PyPDF2
from fastapi import (APIRouter, Depends, File, Form, HTTPException, Path,
                     Query, UploadFile, status)
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

import constant.ai as constant
import constant.config as minio_constant
from app.dto import address, job, minio, resume
from app.factory.factory import RepositoryFactory as factory
from config import postgres
from config.postgres import PostgresDB
from constant import config as cfg
from models.ccp_application import Application
from pkg.logging import logger

# from config.es import ElasticSearchDB as es

class JobRouter:
    def __init__(self):
        self.job_qdrant_repo = factory.get_job_qdrant_repo()
        self.job_weaviate_repo = factory.get_job_weaviate_repo()
        self.resume_qdrant_repo = factory.get_resume_qdrant_repo()
        self.job_repo = factory.get_job_repo()
        self.jobtag_repo = factory.get_jobtag_repo()
        self.minio_repo = factory.get_minio_repo()
        self.application_repo = factory.get_application_repo()
        self.resume_repo = factory.get_resume_repo()
        self.candidate_repo = factory.get_candidate_repo()
        self.address_repo = factory.get_address_repo()
        self.ai_helper = factory.get_ai_helper()
        self.kafka_producer = factory.get_kafka_producer()

        self.router = APIRouter(prefix="/api", tags=['Job'])
        self.router.add_api_route("/jobs", self.list_jobs_from_qdrant, methods=["GET"], response_model=job.ListJobResponse)
        self.router.add_api_route("/related-jobs", self.list_related_jobs_from_qdrant, methods=["GET"], response_model=job.ListRelatedJobResponse)
        self.router.add_api_route("/recommend-jobs", self.list_recommend_jobs_from_qdrant, methods=["GET"], response_model=job.ListRelatedJobResponse)
        self.router.add_api_route("/job", self.get_job_from_qdrant, methods=["GET"], response_model=job.JobAggregate)
        self.router.add_api_route("/job/create", self.create, methods=["POST"], response_model=job.CreateJobPostResponse)
        self.router.add_api_route("/job/apply", self.apply, methods=["POST"], response_model=job.ApplyJobResponse)
        self.router.add_api_route("/job/close", self.close, methods=["POST"], response_model=job.CloseJobResponse)
        self.router.add_api_route("/job/update", self.update_job, methods=["PUT"]) # TODO: , response_model=job.UpdateJobResponse
        self.router.add_api_route("/job/{id}/resumes", self.list_resumes_from_qdrant, methods=["GET"], response_model=resume.ListResumeResponse)
        self.router.add_api_route("/job/check-saved-or-applied", self.check_is_saved_or_applied, methods=["POST"], response_model=job.CheckAppliedOrSavedResponse)

    async def list_jobs_from_qdrant(
        self,
        page: Optional[int] = Query(None, description="Page number"),
        size: Optional[int] = Query(None, description="Page size"),
        input: Optional[str] = Query(None, description="Input text for vector search"),
        job_type: Optional[str] = Query(None, description="Job type filter"),
        company_type: Optional[str] = Query(None, description="Company type filter"),
        last_updated: Optional[str] = Query(None, description="Last updated filter"),
        salary_from: Optional[float] = Query(None, description="Minimum salary filter"),
        salary_to: Optional[float] = Query(None, description="Maximum salary filter"),
        hiring_level: Optional[str] = Query(None, description="Hiring level filter"),
        work_place: Optional[str] = Query(None, description="Work place filter"),    
        applied_count: Optional[int] = Query(None, description="Applied count filter"),
        job_tags: Optional[str] = Query(None, description="Job tags filter"),
        city_name: Optional[str] = Query(None, description="City name filter"),
        country_name: Optional[str] = Query(None, description="Country name filter"),
        search_type: Optional[str] = Query(None, description="Search type: 'vector' or 'hybrid'"),
        salary:  Optional[str] = Query(None, description="Salary range (multile range)"),
        is_hiring:  Optional[bool] = Query(True, description="Is hiring"),
        alpha:  Optional[float] = Query(None, description="Alpha (config for hybrid search)"),
        resume_id: Optional[int] = Query(None, description="Resume id"),
        db: Session = Depends(PostgresDB.get_db)
    ):
        # map query params to req
        try:
            req = job.ListJobRequest(
                page=page,
                size=size,
                input=input,
                job_type=job_type,
                company_type=company_type,
                last_updated=last_updated,
                salary_from=salary_from,
                salary_to=salary_to,
                hiring_level=hiring_level,
                applied_count=applied_count,
                job_tags=job_tags,
                city_name=city_name,
                country_name=country_name,
                work_place=work_place,
                salary=salary,
                is_hiring=is_hiring,
                alpha=alpha,
            )

            if search_type == "vector": # handle vector search
                latest_job =  await self.job_repo.get_latest_job(db=db)
                req.latest_job_id = latest_job.id

                if resume_id is not None: 
                    resume_vector = await self.resume_qdrant_repo.get_resume_vector(resume_id=resume_id)

                    req.vectors = resume_vector if resume_vector is not None else None

                if input is not None:
                    vectors = await self.ai_helper.get_embedding(input)
                    req.vectors = vectors.tolist() if vectors is not None else None

                data = await self.job_qdrant_repo.list_jobs(input=req)

                return data
            elif search_type == "hybrid": # handle hybrid search
                data = await self.job_weaviate_repo.list_jobs(input=req)

                return data
            # elif search_type == "fulltext": # handle full-text search
            #     # data = job_es_repo.list_jobs(input=req)
            else:
                return job.ListJobResponse(
                    count=0,
                    page=req.page,
                    size=req.size,
                    records=list[job.JobAggregate]
                )

        except Exception:
            logger.error(f"list_jobs_from_qdrant failed error = {traceback.format_exc()}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str("Oops, sorry, our server went wrong"))
    

    async def list_related_jobs_from_qdrant(
        self,
        page: Optional[int] = Query(None, description="Page number"),
        size: Optional[int] = Query(None, description="Page size"),
        job_id: Optional[int] = Query(None, description="Job id"),
    ):
        
        # map query params to req
        try:
            req = job.ListRelatedJobRequest(
                job_id=job_id,
                page=page,
                size=size
            )

            data = await self.job_qdrant_repo.list_related_jobs(req)

            return data

        except Exception:
            logger.error(f"list_related_jobs_from_qdrant failed error = {traceback.format_exc()}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str("Oops, sorry, our server went wrong"))
        
    async def list_recommend_jobs_from_qdrant(
        self,
        page: Optional[int] = Query(None, description="Page number"),
        size: Optional[int] = Query(None, description="Page size"),
        user_id: Optional[int] = Query(None, description="User id"),
        db: Session = Depends(PostgresDB.get_db),
    ):
        
        # map query params to req
        try:
            # NOTE: Should we get from qdrant instead of gettin from db? Because in case that resume is existed in db but not in qdrant, the api will return error
            # get all user resumes
            resumes = await self.resume_repo.get_by_user_id(db=db, user_id=user_id)

            resume_ids = []
            for resume in resumes:
                resume_ids.append(resume.id)

            req = job.ListRecommendJobRequest(
                page=page,
                size=size,
                resume_ids=resume_ids
            )

            data = await self.job_qdrant_repo.list_recommend_jobs(req)

            return data

        except Exception:
            logger.error(f"list_recommend_jobs_from_qdrant failed error = {traceback.format_exc()}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str("Oops, sorry, our server went wrong"))

    async def get_job_from_qdrant(
        self,
        id: int = Query(None, description="Job ID"),
        user_id: Optional[int] = Query(None, description="User ID"),
    ):
        try:
            req = job.GetJobRequest(
                id=id,
            )

            data = await self.job_qdrant_repo.get_job(input=req)

            # TODO: push message to kafka
            payload = {
                "user_id": user_id,
                "job_id": id
            }

            self.kafka_producer.produce_message(cfg.KAFKA_TOPIC_JOB_VIEW, payload)

            return data
        except Exception:
            logger.error(f"get_job_from_qdrant failed error = {traceback.format_exc()}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str("Oops, sorry, our server went wrong"))

    async def create(
            self,
            job_title: str = Form(None),
            is_hiring: str = Form(None),
            opened_date: str = Form(None),
            closed_date: str = Form(None),
            salary_from: str = Form(None),
            salary_to: str = Form(None),
            job_type: str = Form(None),
            company_type: str = Form(None),
            address_detail: str = Form(None),
            city_id: str = Form(None),
            recruiter_id: str = Form(None),
            hiring_level: str = Form(None),
            work_place: str = Form(None),
            tags: str = Form(None),
            file: UploadFile = File(None),
            session: Session = Depends(postgres.PostgresDB.get_db),
        ):

        try:
            file_content = await file.read()

            temp_dir = os.path.dirname(os.path.abspath(__file__))
            temp_file_path = os.path.join(temp_dir, file.filename)
            with open(temp_file_path, "wb") as temp_file:
                temp_file.write(file_content)

            # Generate file name
            file_name = str(uuid.uuid4()) + "_" + file.filename

            # Upload file to MinIO and get the public URL
            upload_response = await self.minio_repo.upload(
                minio.UploadMinioRequest(bucket_name=minio_constant.MINIO_BUCKET_JOB, temp_path=temp_file_path, file_name=file_name)
            )
            public_url = upload_response.url

            os.remove(temp_file_path)

            now = datetime.now()
            
            common_job_title = await self.ai_helper.get_common_job_title(job_title, constant.COMMON_JOB_TITLE_PROMPT)

            record = job.JobBase(
                job_title=job_title,
                common_job_title=common_job_title,
                content_url=public_url,
                is_hiring=is_hiring,
                opened_date=opened_date,
                closed_date=closed_date,
                salary_from=salary_from,
                salary_to=salary_to,
                job_type=job_type,
                work_place=work_place,
                company_type=company_type,
                recruiter_id=recruiter_id,
                hiring_level=hiring_level,
                file_name=file_name,
                created_at=now,
                updated_at=now,
            )

            if file is not None:
                # Extract text with formatting from PDF using PyMuPDF
                pdf_file = BytesIO(file_content)

                pdf_document = fitz.open(stream=pdf_file, filetype="pdf")

                markdown_content = pymupdf4llm.to_markdown(pdf_document)

                markdown_content = markdown_content.replace('\n--\n', '\n')
                markdown_content = re.sub(r'\n-+\n', '\n', markdown_content)
                
                record.display_content = markdown_content

                # get text content from pdf
                pdf_reader = PyPDF2.PdfReader(pdf_file)

                text_content = ""
                for page_num in range(len(pdf_reader.pages)):
                    text = pdf_reader.pages[page_num].extract_text()
                    text = text.replace('\x00', '').replace('\n', '').replace('\r', '').replace('\t', '').replace('\x1b', '')
                    text_content += text

                record.content = text_content

            with session.begin():
                try:
                    address_record = None
                    #If they are both None -> Not create a new address record in db
                    if (address_detail is not None) or (city_id is not None):
                        address_record = address.AddressBase(
                            created_at=now,
                            updated_at=now
                        )
                        
                        if address_detail is not None:
                            address_record.detailed_address = address_detail

                        if city_id is not None:
                            address_record.city_id = city_id

                        address_rec = await self.address_repo.create(session, address_record)
                        #Add new address record to a new job
                        record.address_id = address_rec.id

                    #Create new job
                    job_rec = await self.job_repo.create(session, record)

                    if tags is not None:
                        tags = tags.split(',')

                        for tag_id in tags:
                            await self.jobtag_repo.create(session, tag_id=int(tag_id), job_id=job_rec.id)

                    return job.CreateJobPostResponse()

                except SQLAlchemyError:
                    session.rollback()
                    logger.error(f"create_job failed error = {traceback.format_exc()}")
                    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str("Oops, sorry, our server went wrong"))

        except Exception:
            logger.error(f"create_job failed error = {traceback.format_exc()}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str("Oops, sorry, our server went wrong"))
        finally:
            if file is not None:
                file.file.close()

    async def list_resumes_from_qdrant(
            self,
            id: int = Path(..., title="Job ID"),
            page: Optional[int] = Query(None, description="Page numeber"),
            size: Optional[int] = Query(None, description="Page size")
        ):
        try:
            req = resume.ListResumeRequest(
                page=page,
                size=size,
                job_id=id
            )
            data = await self.resume_qdrant_repo.list_resumes(input=req)
            return data
        except Exception:
            logger.error(f"list_resumes_from_qdrant failed error = {traceback.format_exc()}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str("Oops, sorry, our server went wrong"))

    async def apply(
            self,
            req: Optional[job.ApplyJobRequest], 
            session: Session = Depends(postgres.PostgresDB.get_db)
        ):
        try:
            now = datetime.now()

            record = Application(
                resume_id=req.resume_id,
                job_id=req.job_id,
                created_at=now,
                updated_at=now
            )

            session.autocommit = False # TODO: remove this?
            with session.begin():
                try:
                    await self.application_repo.create(session, record)

                    return job.ApplyJobResponse()
                
                except IntegrityError:
                    session.rollback()
                    logger.error(f"apply_job failed error [IntegrityError] = {traceback.format_exc()}")
                    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="You have already applied for this job.")
                except SQLAlchemyError:
                    session.rollback()
                    logger.error(f"apply_job failed error [SQLAlchemyError] = {traceback.format_exc()}")
                    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str("Oops, sorry, our server went wrong"))

        except Exception:
            logger.error(f"apply_job failed error = {traceback.format_exc()}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str("Oops, sorry, our server went wrong"))

    async def close(
            self,
            #req: Optional[job.CloseJobRequest], 
            job_id: int = Form(None),
            session: Session = Depends(postgres.PostgresDB.get_db)
        ):
        try:
            now = datetime.now()

            #data = job_repo.get_by_id(req.job_id)

            props = {
                "is_hiring": False,
                'updated_at': now,
                'closed_date': now,
            }

            session.autocommit = False # TODO: remove this?
            with session.begin():
                try:
                    await self.job_repo.update_with_map(db=session, job_id=job_id, props=props)
                    return job.CloseJobResponse(message="Closed job succesfully!")
                    # job_repo.update_with_map(session, data, props)

                except SQLAlchemyError:
                    session.rollback()
                    logger.error(f"close_job failed error [SQLAlchemyError] = {traceback.format_exc()}")
                    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str("Oops, sorry, our server went wrong"))
                
        except Exception:
            logger.error(f"close_job failed error = {traceback.format_exc()}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str("Oops, sorry, our server went wrong"))

    async def update_job(
        self,
        job_id: int = Form(None),
        job_title: str = Form(None),
        new_job_title: str = Form(None) , #None if there is no change
        opened_date: str = Form(None) ,
        closed_date: str = Form(None) ,
        salary_from: str = Form(None) ,
        salary_to: str = Form(None) ,
        job_type: str = Form(None) ,
        company_type: str = Form(None) ,
        address_id: str = Form(None) , # TODO: Use city_id and country_id instead of address_id, example: replace by: city_id: str = Form(None), country_id: str = Form(None)
        address_detail: str = Form(None),
        city_id: str = Form(None),
        hiring_level: str = Form(None), 
        work_place: str = Form(None) ,
        tags: str = Form(None),
        file: UploadFile = File(None),
        session: Session = Depends(postgres.PostgresDB.get_db),
    ):
        try:
            now = datetime.now()
            
            #Remove jobtags
            await self.jobtag_repo.delete_jobtags(db=session, job_id=job_id)
            #Update jobtags
            with session.begin():
                try:
                    tags = tags.split(',')
                    for tag_id in tags:
                        await self.jobtag_repo.create(session, tag_id=int(tag_id), job_id=job_id)
                
                except IntegrityError:
                    session.rollback()
                    logger.error(f"create jobtags failed error [IntegrityError] = {traceback.format_exc()}")
                    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Jobtags create failed.")


            #Update address
            a_props = {
                "city_id": city_id,
                "detailed_address": address_detail,
                "updated_at": now
            }

            props = {
                "job_title": job_title,
                "opened_date": opened_date,
                "closed_date": closed_date,
                "salary_from": salary_from,
                "salary_to": salary_to,
                "job_type": job_type,
                "company_type": company_type,
                "hiring_level": hiring_level,
                "work_place": work_place,
                "updated_at": now,
            }

            # Change common_job_title if change job_title
            if new_job_title is not None:
                common_job_title = await self.ai_helper.get_common_job_title(job_title, constant.COMMON_JOB_TITLE_PROMPT)
                props["common_job_title"] = common_job_title

            if file is not None:
                #Get file name
                file_name = await self.job_repo.get_file_name(db=session, job_id=job_id)

                #Delete file in minio
                await self.minio_repo.remove_object(bucket_name=minio_constant.MINIO_BUCKET_JOB, file_name=file_name)


                file_content = await file.read()

                temp_dir = os.path.dirname(os.path.abspath(__file__))

                temp_file_path = os.path.join(temp_dir, file.filename)
                with open(temp_file_path, "wb") as temp_file:
                    temp_file.write(file_content)

                #Generate file name
                new_file_name  = str(uuid.uuid4())+"-"+file.filename

                url = await self.minio_repo.upload(
                    minio.UploadMinioRequest(bucket_name=minio_constant.MINIO_BUCKET_JOB, temp_path=temp_file_path, file_name=new_file_name)
                )

                os.remove(temp_file_path)

                #Get content from pdf
                pdf_file = BytesIO(file_content)

                pdf_reader = PyPDF2.PdfReader(pdf_file)

                text_content = ""
                for page_num in range(len(pdf_reader.pages)):
                    text_content += pdf_reader.pages[page_num].extract_text()

                props["content"] = text_content
                props["content_url"] = url.url
                props["file_name"] = new_file_name
            

            try:
                #update address
                await self.address_repo.update_with_map(db=session, address_id=address_id, props=a_props)

                #update job
                await self.job_repo.update_with_map(db=session, job_id=job_id, props=props)

            except SQLAlchemyError:
                session.rollback()
                logger.error(f"update_job failed error [SQLAlchemyError] = {traceback.format_exc()}")
                raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str("Oops, sorry, our server went wrong"))
            
        except Exception:
            logger.error(f"update_job failed error = {traceback.format_exc()}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str("Oops, sorry, our server went wrong"))
        
    
    async def check_is_saved_or_applied(
        self,
        req: Optional[job.CheckAppliedOrSavedRequest],
        db: Session = Depends(postgres.PostgresDB.get_db)
    ):
        try:
            req = job.CheckAppliedOrSavedRequest(
                user_id=req.user_id,
                job_id=req.job_id
            )

            # Check whether this user applied to this job or not
            resumes = await self.resume_repo.get_by_user_id(db=db, user_id=req.user_id)
            resume_ids = []
            for resume in resumes:
                resume_ids.append(resume.id)

            applications = await self.application_repo.list_by_resume_ids(db=db, resume_ids=resume_ids, job_id=req.job_id)

            # Check whether this user saved this job or not
            job_saved = await self.candidate_repo.get_job_saved_by_candidate_id(db=db, user_id=req.user_id, job_id=req.job_id)

            resp = job.CheckAppliedOrSavedResponse()

            if len(applications) > 0:
                resp.is_applied = True

            if job_saved is not None:
                resp.is_saved = True

            return resp
        except Exception:
            logger.error(f"check_is_saved_or_applied failed error = {traceback.format_exc()}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str("Oops, sorry, our server went wrong"))

job_router = JobRouter().router