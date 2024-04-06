from config.postgres import SessionLocal

from models.ccp_candidate import Candidate
from models.ccp_resume import Resume
from models.ccp_application import Application
from models.ccp_job import Job
from app.dto import candidate
class CandidateRepository:
    def __init__(self):
        self.db = SessionLocal()
        
    def get_by_id(self, id):
        return self.db.query(Candidate).filter(Candidate.id == id).first()
    
    def get_applied_jobs(self, id) -> candidate.ListAppliedJobsResponse:
        applications = self.db.query(Application.job_id, Application.resume_id, Job.job_title, Application.created_at, Application.updated_at)\
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
                    created_at=app.created_at,
                    updated_at=app.updated_at
                )
            )
        return candidate.ListAppliedJobsResponse(
            records=records
        )