from config.postgres import SessionLocal

from models.ccp_candidate import Candidate
from models.ccp_resume import Resume
from models.ccp_application import Application
from models.ccp_job_saved import JobSaved
from models.ccp_job import Job
from app.dto import candidate
class CandidateRepository:
    def __init__(self):
        self.db = SessionLocal()
        
    def get_by_id(self, id):
        return self.db.query(Candidate).filter(Candidate.id == id).first()
    
    def get_applied_jobs(self, id) -> candidate.ListAppliedJobsResponse:
        applications = self.db.query(Application.job_id, Application.resume_id, Job.job_title, Job.content, Job.is_hiring, Job.opened_date, Job.closed_date, 
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
    
    def create_saved_job(self, record: JobSaved) -> JobSaved:
        self.db.add(record)
        self.db.commit()
        return record

    def delete_saved_job(self, record: JobSaved) -> candidate.UpdateSaveJobResponse:
        self.db.query(JobSaved).filter_by(candidate_id=record.candidate_id, job_id=record.job_id).delete()
        self.db.commit()

    def get_saved_jobs(self, id) -> candidate.ListSavedJobsResponse:
        jobs = self.db.query(JobSaved.job_id, Job.job_title, Job.content, Job.is_hiring, Job.opened_date, Job.closed_date, 
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
    def get_job_saved_by_candidate_id(self, user_id, job_id) -> JobSaved:
        result = self.db.query(JobSaved).filter(JobSaved.candidate_id==user_id, JobSaved.job_id==job_id).first()
        
        return result