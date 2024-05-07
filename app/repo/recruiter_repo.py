from config.postgres import SessionLocal
from models.ccp_job import Job
from app.dto import recruiter

class RecruiterRepository:
    def __init__(self):
        self.db = SessionLocal()
        
    def get_jobs_posted(self, id) -> recruiter.ListJobsPostedResponse:
        result =  self.db.query(Job.id, Job.job_title, Job.content, Job.is_hiring, Job.opened_date, Job.closed_date, 
                                Job.salary_from, Job.salary_to, Job.job_type, Job.work_place,
                                 Job.company_type, Job.hiring_level, Job.created_at, Job.updated_at, Job.applied_count).filter(Job.recruiter_id == id).all()
        record = []
        for job in result:
            record.append(
                recruiter.JobPostedResponse(
                    job_id=job.id,
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
                    updated_at=job.updated_at,
                    applied_count=job.applied_count
                )
            )
        
        return recruiter.ListJobsPostedResponse (records=record)
        
    