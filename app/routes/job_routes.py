from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter, Query, Path, UploadFile, File, Form
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
import PyPDF2
from typing import List, Optional
import os
from io import BytesIO
import uuid


from config.postgres import SessionLocal
from config import postgres
from config.qdrant import QdrantVDB as qdrant
# from config.es import ElasticSearchDB as es

from datetime import datetime

# from app.repo.job_es_repo import JobESRepository
from app.repo.job_qdrant_repo import JobQdrantRepository
from app.repo.job_weaviate_repo import JobWeaviateRepository
from app.repo.job_repo import JobRepository 
from app.repo.jobtags_repo import JobTagsRepository
from app.repo.resume_qdrant_repo import ResumeQdrantRepository
from app.repo.job_minio_repo import JobMinioRepository
from app.repo.application_repo import ApplicationRepository

from models.ccp_application import Application

from app.dto import job
from app.dto import resume
from app.dto import application

from app.ai.ai_helper import AI

import constant.ai as constant

job_router = APIRouter(
    prefix="/api",
    tags=['Job']
)

# job_es_repo = JobESRepository(index_name=es.ES_INDEX_JOB_SEARCH)
job_qdrant_repo = JobQdrantRepository(index_name=qdrant.QDRANT_INDEX_JOB_SEARCH)
job_weaviate_repo = JobWeaviateRepository(collection_name="Job")
resume_qdrant_repo = ResumeQdrantRepository(index_name=qdrant.QDRANT_INDEX_RESUME_SEARCH)
job_repo = JobRepository()
jobtag_repo = JobTagsRepository()
job_minio_repo = JobMinioRepository()
application_repo = ApplicationRepository()

ai_helper = AI()

@job_router.get("/jobs", response_model=job.ListJobResponse)
def list_jobs_from_qdrant(
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

        # get latest id

        if search_type == "vector": # handle vector search
            if input is not None:
                vectors = ai_helper.get_embedding(input)
                req.vectors = vectors.tolist() if vectors is not None else None

            data = job_qdrant_repo.list_jobs(input=req)

            return data
        elif search_type == "hybrid": # handle hybrid search
            data = job_weaviate_repo.list_jobs(input=req)

            return data
        # elif search_type == "fulltext": # handle full-text search
        #     # data = job_es_repo.list_jobs(input=req)
        else:
            return job.ListJobResponse(
                count=0,
                page=req.size,
                size=req.size,
                records=list[job.JobAggregate]
            )

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    
@job_router.get("/job", response_model=job.JobAggregate)
def get_job_from_qdrant(
    id: Optional[int] = Query(None, description="Job ID"),
):
    try:
        req = job.GetJobRequest(
            id=id
        )

        # TODO: check whether this user is save or applied to this job or not
        # Step 1: Get resume_ids by user_id
        # Step 2: Query to check

        data = job_qdrant_repo.get_job(input=req)
        return data
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@job_router.post("/job/create", response_model=job.CreateJobPostResponse)
async def create(
        job_title: str = Form(None),
        content: str = Form(None) ,
        is_hiring: str = Form(None) ,
        opened_date: str = Form(None) ,
        closed_date: str = Form(None) ,
        salary_from: str = Form(None) ,
        salary_to: str = Form(None) ,
        job_type: str = Form(None) ,
        company_type: str = Form(None) ,
        address_id: str = Form(None) ,
        recruiter_id: str = Form(None) ,
        hiring_level: str = Form(None), 
        work_place: str = Form(None) ,
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

        url = job_minio_repo.upload_job_to_minio(input=job.UploadJobMinioRequest(temp_path=temp_file_path, file_name=str(uuid.uuid4())+"-"+file.filename))
        presigned_url = job_minio_repo.generate_presigned_url(object_name=str(url))

        os.remove(temp_file_path)

        now = datetime.now()
        
        common_job_title = ai_helper.get_common_job_title(job_title, constant.COMMON_JOB_TITLE_PROMPT)

        record = job.JobBase(
            job_title=job_title,
            common_job_title=common_job_title,
            content_url=presigned_url,
            is_hiring=is_hiring,
            opened_date=opened_date,
            closed_date=closed_date,
            salary_from=salary_from,
            salary_to=salary_to,
            job_type=job_type,
            work_place=work_place,
            company_type=company_type,
            address_id=address_id,
            recruiter_id=recruiter_id,
            hiring_level=hiring_level,
            created_at=now,
            updated_at=now,
        )
        print("STOP")
        if file is not None:
            pdf_file = BytesIO(file_content)

            pdf_reader = PyPDF2.PdfReader(pdf_file)

            text_content = ""
            for page_num in range(len(pdf_reader.pages)):
                text_content += pdf_reader.pages[page_num].extract_text()

            record.content = text_content


        session.autocommit = False # TODO: remove this?
        with session.begin():
            try:
                job_rec = job_repo.create(session, record)

                if tags is not None:
                    tags = tags.split(',')

                    for tag_id in tags:
                        jobtag_repo.create(session, tag_id=int(tag_id), job_id=job_rec.id)

                return job.CreateJobPostResponse()

            except SQLAlchemyError as e:
                session.rollback()
                raise e

    except Exception:
        return {"message": "There was an error creating or processing the PDF file"}

    finally:
        session.close()
        if file is not None:
            file.file.close()

@job_router.get("/job/{id}/resumes", response_model=resume.ListResumeResponse)
def list_resumes_from_qdrant(
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
        data = resume_qdrant_repo.list_resumes(input=req)
        return data
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    

@job_router.post("/job/apply", response_model=job.ApplyJobResponse)
def apply(
        req: Optional[job.ApplyJobRequest], 
        session: Session = Depends(postgres.PostgresDB.get_db)
    ):
    # try:
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
                application_repo.create(session, record)

                return job.ApplyJobResponse()
            
            except IntegrityError as e:
                session.rollback()
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="You have already applied for this job.")
            except SQLAlchemyError as e:
                session.rollback()
                raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # except Exception as e:
    #     raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    

@job_router.post("/job/close", response_model=job.CloseJobResponse)
def apply(
        req: Optional[job.CloseJobRequest], 
        session: Session = Depends(postgres.PostgresDB.get_db)
    ):
    try:
        now = datetime.now()

        data = job_repo.get_by_id(req.job_id)

        props = {
            "is_hiring": False,
            'updated_at': now,
            'closed_date': now,
        }

        session.autocommit = False # TODO: remove this?
        with session.begin():
            try:
                job_repo.update_with_map(data, props)

            except SQLAlchemyError as e:
                session.rollback()
                raise e
            
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@job_router.get("/qdrant/health-check")
async def root():
    return {"message": "Good"}