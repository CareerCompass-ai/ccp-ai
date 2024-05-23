from config.postgres import SessionLocal
from sqlalchemy.orm import Session

from models.ccp_candidate import Candidate
from models.ccp_resume import Resume
from models.ccp_application import Application
from models.ccp_job_saved import JobSaved
from models.ccp_job import Job
from models.ccp_viewedjob import ViewedJob

from app.dto import candidate

class CandidateRepository:      
    async def get_by_id(self, db:Session, id):
        return db.query(Candidate).filter(Candidate.id == id).first()
    
    async def get_applied_jobs(self, db:Session, id) -> candidate.ListAppliedJobsResponse:
        applications = db.query(Application.job_id, Application.resume_id, Job.job_title, Job.content, Job.is_hiring, Job.opened_date, Job.closed_date, 
                                     Job.salary_from, Job.salary_to, Job.job_type, Job.work_place, Job.company_type, Job.hiring_level, Application.created_at, Application.updated_at)\
            .join(Resume, Application.resume_id == Resume.id)\
            .join(Job, Application.job_id == Job.id)\
            .filter(Resume.candidate_id == id)\
            .order_by(Application.created_at.desc())\
            .all()
        records = []
        for app in applications:
            records.append(
                candidate.AppliedJobsResponse(
                    job_id=app.job_id,
                    resume_id=app.resume_id,
                    job_title=app.job_title,
                    content=app.content,
                    is_hiring=app.is_hiring,
                    opened_date=app.opened_date,
                    closed_date=app.closed_date,
                    salary_from=app.salary_from,
                    salary_to=app.salary_to,
                    job_type=app.job_type,
                    work_place=app.work_place,
                    company_type=app.company_type,
                    hiring_level=app.hiring_level,
                    created_at=app.created_at,
                    updated_at=app.updated_at
                )
            )

        return candidate.ListAppliedJobsResponse(
            records=records
        )
    
    async def create_saved_job(self, db:Session, record: JobSaved) -> JobSaved:
        db.add(record)
        db.commit()

        return record

    async def delete_saved_job(self, db:Session, record: JobSaved) -> candidate.UpdateSaveJobResponse:
        db.query(JobSaved).filter_by(candidate_id=record.candidate_id, job_id=record.job_id).delete()
        db.commit()

    async def get_saved_jobs(self, db:Session, id) -> candidate.ListSavedJobsResponse:
        jobs = db.query(JobSaved.job_id, Job.job_title, Job.content, Job.is_hiring, Job.opened_date, Job.closed_date, 
                             Job.salary_from, Job.salary_to, Job.job_type, Job.work_place, Job.company_type, Job.hiring_level, JobSaved.created_at, JobSaved.updated_at)\
            .join(JobSaved, Job.id == JobSaved.job_id)\
            .filter(JobSaved.candidate_id == id)\
            .order_by(JobSaved.created_at.desc())\
            .all()
        records = []
        for job in jobs:
            records.append(
                candidate.SavedJobsResponse(
                    job_id=job.job_id,
                    job_title=job.job_title,
                    content=job.content,
                    is_hiring=job.is_hiring,
                    opened_date=job.opened_date,
                    closed_date=job.closed_date,
                    salary_from=job.salary_from,
                    salary_to=job.salary_to,
                    job_type=job.job_type,
                    work_place=job.work_place,
                    company_type=job.company_type,
                    hiring_level=job.hiring_level,
                    created_at=job.created_at,
                    updated_at=job.updated_at
                )
            )
        
        return candidate.ListSavedJobsResponse(
            records=records
        )
    
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
