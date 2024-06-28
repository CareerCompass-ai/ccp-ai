import traceback
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List
from app.dto import recruiter, resume, job
from app.factory.factory import RepositoryFactory as factory
from config.postgres import PostgresDB
from models.ccp_talent_saved import TalentSaved
from pkg.logging import logger


class RecruiterRouter:
    def __init__(self):
        self.recruiter_repo = factory.get_recruiter_repo()
        self.resume_qdrant_repo = factory.get_resume_qdrant_repo()
        self.talent_repo = factory.get_talent_saved_repo()
        self.job_qdrant_repo = factory.get_job_qdrant_repo()
        self.router = APIRouter(prefix="/api", tags=['Recruiter'])
        self.router.add_api_route("/recruiter/jobs-posted", self.list_jobs_posted, methods=["GET"], response_model=recruiter.ListJobsPostedAggregate)
        self.router.add_api_route("/recruiter/update-saved-talent", self.update_saved_talent, methods=["PUT"], response_model=recruiter.SaveTalentResponse)
        self.router.add_api_route("/recruiter/candidates-saved", self.list_candidates_saved, methods=["GET"], response_model=recruiter.ListCandidatesSaved)

    async def list_jobs_posted(
        self,
        recruiter_id: int = Query(None, description="recruiter ID"),
        page: int = Query(None, description="Page"),
        size: int = Query(None, description="Size"),
        db: Session = Depends(PostgresDB.get_db)
    ):
        try:
            if page <= 0:
                page = 1
            if size <= 0:
                size = 10
            if size >= 100:
                size = 100

            job_ids = await self.recruiter_repo.get_jobs_posted(db=db, id=recruiter_id)
            total_records = len(job_ids)

            offset = (page - 1) * size

            paging_list = job_ids[offset:offset+size]

            data = await self.job_qdrant_repo.list_jobs_by_ids(ids=paging_list)
            return recruiter.ListJobsPostedAggregate(
                count=total_records,
                page=page,
                size=size,
                records=data
            )
        except Exception:
            logger.error(f"list_jobs_posted failed error = {traceback.format_exc()}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str("Oops, sorry, our server went wrong"))

    async def update_saved_talent(
        self,
        req: recruiter.SaveTalentRequest,
        db: Session = Depends(PostgresDB.get_db)
    ):
        try:
            now = datetime.now()
            record = TalentSaved(
                recruiter_id=req.recruiter_id,
                candidate_id=req.candidate_id,
                resume_id=req.resume_id,
                created_at=now,
                updated_at=now
            )

            if req.type == 1:
                await self.talent_repo.create_saved_talent(db=db, record=record)
                return recruiter.SaveTalentResponse(msg="Save Talent Successfully!")

            elif req.type == 2:
                await self.talent_repo.delete_saved_talent(db=db, record=record)
                return recruiter.SaveTalentResponse(msg="Unsave Talent Successfully!")

        except Exception:
            logger.error(f"update_saved_tent failed error = {traceback.format_exc()}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str("Oops, sorry, our server went wrong"))

    async def list_candidates_saved(
        self,
        recruiter_id: int = Query(None, description="recruiter ID"),
        page: int = Query(None, description="Page"),
        size: int = Query(None, description="Size"),
        db: Session = Depends(PostgresDB.get_db)
    ):
        try:
            if page <= 0:
                page = 1
            if size <= 0:
                size = 10
            if size >= 100:
                size = 100

            #Return list of ids order by created_at desc
            resume_ids = await self.recruiter_repo.get_talents_saved(db=db, id=recruiter_id)
            total_records = len(resume_ids)

            offset = (page - 1) * size

            paging_list = resume_ids[offset:offset+size]

            data = await self.resume_qdrant_repo.list_resumes_by_ids(resume_ids=paging_list)
            return recruiter.ListCandidatesSaved(
                count=total_records,
                page=page,
                size=size,
                records=data
            )
        except Exception:
            logger.error(f"list_candidates_saved failed error = {traceback.format_exc()}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str("Oops, sorry, our server went wrong"))


recruiter_router = RecruiterRouter().router