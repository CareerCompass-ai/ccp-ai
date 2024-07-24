from sqlalchemy.orm import Session

from app.dto import candidate
from models.ccp_application import Application
from models.ccp_candidate import Candidate
from models.ccp_job import Job
from models.ccp_job_saved import JobSaved
from models.ccp_resume import Resume
from models.ccp_viewedjob import ViewedJob

from typing import List
class CandidateRepository:      
    async def get_by_id(self, db:Session, id):
        return db.query(Candidate).filter(Candidate.id == id).first()
    
    async def get_applied_jobs(self, db: Session, candidate_id: int, input: str, offset: int, limit: int) -> candidate.ListResumesAppliedResponse:
        query = db.query(Application.job_id, Application.resume_id, Resume.resume_link)\
                .join(Resume, Application.resume_id == Resume.id)\
                .join(Job, Application.job_id == Job.id)\
                .filter(Resume.candidate_id == candidate_id)
        
        if input:
            query = query.filter(Job.job_title.ilike(f"%{input}%"))
        
        total_records = query.count()

        applications = query.order_by(Application.updated_at.desc())\
                            .offset(offset).limit(limit).all()
        
        records = [
            candidate.ResumesAppliedResponse(
                job_id=app.job_id,
                resume_id=app.resume_id,
                resume_url=app.resume_link
            )
            for app in applications
        ]
        
        return candidate.ListResumesAppliedResponse(count=total_records, records=records)
    
    async def create_saved_job(self, db:Session, record: JobSaved) -> JobSaved:
        db.add(record)
        db.commit()

        return record

    async def delete_saved_job(self, db:Session, record: JobSaved) -> candidate.UpdateSaveJobResponse:
        db.query(JobSaved).filter_by(candidate_id=record.candidate_id, job_id=record.job_id).delete()
        db.commit()

    async def get_saved_jobs(self, db: Session, candidate_id: int, input: str, offset: int, limit: int):
        query = db.query(JobSaved.job_id)\
                .join(Job, JobSaved.job_id == Job.id)\
                .filter(JobSaved.candidate_id == candidate_id)
        
        if input:
            query = query.filter(Job.job_title.ilike(f"%{input}%"))

        total_records = query.count()
        
        jobs = query.order_by(JobSaved.updated_at.desc())\
                    .offset(offset).limit(limit).all()
        
        records = [job.job_id for job in jobs]
        
        return total_records, records
    
    # TODO: Refactor this file
    async def get_job_saved_by_candidate_id(self, db:Session, user_id, job_id) -> JobSaved:
        result = db.query(JobSaved).filter(JobSaved.candidate_id==user_id, JobSaved.job_id==job_id).first()

        return result
    
    async def check_viewed_job(self, db:Session, candidate_id, job_id) -> candidate.JobViewdResponse:
        result = db.query(ViewedJob).filter(ViewedJob.candidate_id == candidate_id, ViewedJob.job_id == job_id).first()
        if result is not None:
            return candidate.JobViewdResponse (
                job_id=result.job_id,
                candidate_id=result.candidate_id,
                time=result.view_datetime
            )

        return result
