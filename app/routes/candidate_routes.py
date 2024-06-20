import traceback
from datetime import datetime
from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.dto import candidate, resume, job
from app.factory.factory import RepositoryFactory as factory
from config.postgres import PostgresDB
from models.ccp_job_saved import JobSaved
from pkg.logging import logger


class CandidateRouter:
    def __init__(self):
        self.candidate_repo = factory.get_candidate_repo()
        self.resume_repo = factory.get_resume_repo()
        self.job_qdrant_repo = factory.get_job_qdrant_repo()
        self.router = APIRouter(prefix="/api", tags=['Candidate'])
        self.router.add_api_route("/candidate/applied", self.list_jobs_applied, methods=["GET"], response_model=candidate.ListAppliedJobsResponse)
        self.router.add_api_route("/candidate/update-saved-job", self.update_saved_job, methods=["PUT"], response_model=candidate.UpdateSaveJobResponse)
        self.router.add_api_route("/candidate/saved-jobs", self.list_jobs_saved, methods=["GET"], response_model=candidate.ListJobsSaved)
        self.router.add_api_route("/resumes", self.list_resume_of_candidate, methods=["GET"], response_model=resume.GetResumesOfCandidateResponse)

    async def list_jobs_applied(
            self, 
            candidate_id: int = Query(None, description="Candidate/User ID"), 
            page: int = Query(None, description="Page"),
            size: int = Query(None, description="Size"),
            db: Session = Depends(PostgresDB.get_db)):
        try:
            if page is None or page <= 0:
                page = 1
            if size is None or size <= 0:
                size = 10
            if size >= 100:
                size = 100

            _response = await self.candidate_repo.get_applied_jobs(db=db, id=candidate_id)

            response = _response.model_dump().get('records')
            
            job_ids = []
            resume_ids = []
            resume_urls = []

            for record in response:
                job_ids.append(record['job_id'])
                resume_ids.append(record['resume_id'])
                resume_urls.append(record['resume_url'])

            total_records = len(job_ids)

            offset = (page - 1) * size

            paged_job_ids = job_ids[offset:offset + size]
            paged_resume_ids = resume_ids[offset:offset + size]
            paged_resume_urls = resume_urls[offset:offset + size]

            data = await self.job_qdrant_repo.list_jobs_applied(paged_job_ids, paged_resume_ids, paged_resume_urls)
            return candidate.ListAppliedJobsResponse(
                count=total_records,
                page=page,
                size=size,
                records=data
            )
        except Exception:
            logger.error(f"list_jobs_applied failed error = {traceback.format_exc()}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Oops, sorry, our server went wrong")

    async def update_saved_job(self, req: candidate.UpdateSaveJobRequest, db: Session = Depends(PostgresDB.get_db)):
        try:
            now = datetime.now()
            record = JobSaved(
                candidate_id=req.candidate_id,
                job_id=req.job_id,
                created_at=now,
                updated_at=now,
            )

            if req.type == 1:
                await self.candidate_repo.create_saved_job(db=db, record=record)
                return candidate.UpdateSaveJobResponse(message="Save job successfully!")
            elif req.type == 2:
                await self.candidate_repo.delete_saved_job(db=db, record=record)
                return candidate.UpdateSaveJobResponse(message="Unsave job successfully")

        except Exception:
            logger.error(f"update_saved_job failed error = {traceback.format_exc()}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Oops, sorry, our server went wrong")

    async def list_jobs_saved(
            self, 
            candidate_id: Optional[int] = Query(None, description="Candidate/User ID"), 
            page: int = Query(None, description="Page"),
            size: int = Query(None, description="Size"),
            db: Session = Depends(PostgresDB.get_db)):
        try:
            if page <= 0:
                page = 1
            if size <= 0:
                size = 10
            if size >= 100:
                size = 100

            job_ids = await self.candidate_repo.get_saved_jobs(db=db, id=candidate_id)

            total_records = len(job_ids)

            offset = (page - 1) * size

            paging_list = job_ids[offset:offset+size]
            
            data = await self.job_qdrant_repo.list_jobs_by_ids(ids=paging_list)
            return candidate.ListJobsSaved(
                count=total_records,
                page=page,
                size=size,
                records=data
            )
        except Exception:
            logger.error(f"list_jobs_saved failed error = {traceback.format_exc()}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Oops, sorry, our server went wrong")

    async def list_resume_of_candidate(self, candidate_id: Optional[int] = Query(None, description="Candidate ID"), db: Session = Depends(PostgresDB.get_db)):
        try:
            data = await self.resume_repo.get_by_user_id(db=db, user_id=candidate_id)

            resume_records = [resume.ResumeBase(
                id=res.id,
                candidate_id=res.candidate_id,
                resume_link=res.resume_link,
                resume_name=res.resume_name,
                created_at=res.created_at,
                updated_at=res.updated_at
            ) for res in data]

            return resume.GetResumesOfCandidateResponse(records=resume_records)
        except Exception:
            logger.error(f"list_resume_of_candidate failed error = {traceback.format_exc()}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Oops, sorry, our server went wrong")


candidate_router = CandidateRouter().router
