import traceback
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.dto import recruiter
from app.factory.factory import RepositoryFactory as factory
from config.postgres import PostgresDB
from models.ccp_talent_saved import TalentSaved
from pkg.logging import logger


class RecruiterRouter:
    def __init__(self):
        self.recruiter_repo = factory.get_recruiter_repo()
        self.talent_repo = factory.get_talent_saved_repo()
        self.project_repo = factory.get_project_repo()
        self.education_repo = factory.get_education_repo()
        self.certificate_repo = factory.get_certificate_repo()
        self.work_experience_repo = factory.get_work_experience_repo()
        self.candidate_repo = factory.get_candidate_repo()
        self.router = APIRouter(prefix="/api", tags=['Recruiter'])
        self.router.add_api_route("/recruiter/jobs-posted", self.list_jobs_posted, methods=["GET"], response_model=recruiter.ListJobsPostedResponse)
        self.router.add_api_route("/recruiter/update-saved-talent", self.update_saved_talent, methods=["PUT"], response_model=recruiter.SaveTalentResponse)
        self.router.add_api_route("/recruiter/candidates-saved", self.list_candidates_saved, methods=["GET"], response_model=recruiter.ListTalentSavedResponse)

    async def list_jobs_posted(
        self,
        recruiter_id: int = Query(None, description="recruiter ID"),
        db: Session = Depends(PostgresDB.get_db)
    ):
        try:
            data = await self.recruiter_repo.get_jobs_posted(db=db, id=recruiter_id)
            return data
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
        db: Session = Depends(PostgresDB.get_db)
    ):
        try:
            _candidate = await self.recruiter_repo.get_talents_saved(db=db, id=recruiter_id)
            record = []
            for candidate in _candidate:
                _detail_info = await self.candidate_repo.get_detail(db=db, id=candidate[1][0])
                detail_info = recruiter.TalentSavedResponse(
                    candidate_id = _detail_info.candidate_id,
                    year_of_experience = _detail_info.year_of_experience,
                    open_to_work = _detail_info.open_to_work,
                    self_introduction = _detail_info.self_introduction,
                    level = _detail_info.level,
                    email = _detail_info.email,
                    phone = _detail_info.phone,
                    first_name = _detail_info.first_name,
                    last_name = _detail_info.last_name,
                    work_title = _detail_info.work_title,
                    gender = _detail_info.gender,
                    dob = _detail_info.dob,
                    detailed_address = _detail_info.detailed_address,
                    city_name = _detail_info.city_name,
                    country_name = _detail_info.country_name
                )

                _projects = await self.project_repo.list_by_candidate_id(db=db, candidate_id=candidate[1][0])
                _certificate = await self.certificate_repo.list_by_candidate_id(db=db, candidate_id=candidate[1][0])
                _education = await self.education_repo.list_by_candidate_id(db=db, candidate_id=candidate[1][0])
                _work_exp = await self.work_experience_repo.list_by_candidate_id(db=db, candidate_id=candidate[1][0])

                detail_info.projects = _projects
                detail_info.certificates = _certificate
                detail_info.educations = _education
                detail_info.work_experiences = _work_exp

                record.append(detail_info)
            return recruiter.ListTalentSavedResponse(records=record)
        except Exception:
            logger.error(f"list_candidates_saved failed error = {traceback.format_exc()}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str("Oops, sorry, our server went wrong"))


recruiter_router = RecruiterRouter().router