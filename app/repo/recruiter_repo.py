from config.postgres import SessionLocal
from models.ccp_job import Job
from app.dto import recruiter

class RecruiterRepository:
    def __init__(self):
        self.db = SessionLocal()
        
    def get_jobs_posted(self, id) -> recruiter.ListJobsPostedResponse:
        result =  self.db.query(Job.id, Job.job_title, Job.created_at, Job.closed_date, Job.applied_count).filter(Job.recruiter_id == id).all()
        record = []
        for job in result:
            record.append(
                recruiter.JobPostedResponse(
                    job_id=job.id,
                    job_title=job.job_title,
                    created_at=job.created_at,
                    closed_date=job.closed_date,
                    applied_count=job.applied_count
                )
            )
        
        return recruiter.ListJobsPostedResponse (record=record)
        
    