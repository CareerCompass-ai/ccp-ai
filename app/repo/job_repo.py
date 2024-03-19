from config.postgres import SessionLocal
from sqlalchemy.orm import Session
from models import ccp_job
from models.ccp_job import Job

from app.dto import job

from typing import List, Optional


class JobRepository:
    def __init__(self):
        self.db = SessionLocal()

    def get_by_id(self, id):
        return self.db.query(Job).filter(Job.id == id).first()
    
    def get_jobs(self, db: Session) -> List[job.JobAggregate]:
        jobs = db.query(Job).all()
        job_aggregates = []
        for item in jobs:
            job_aggregate = job.JobAggregate(
                id=item.id,
                job_title=item.job_title,
                content=item.content,
                content_url=item.content_url,
                is_hiring=item.is_hiring,
                opened_date=item.opened_date,
                closed_date=item.closed_date,
                salary_from=item.salary_from,
                salary_to=item.salary_to,
                job_type=item.job_type,
                company_type=item.company_type,
                matching_score=0.0, 
                user_id=0,  
                user_name="", 
                created_at=item.created_at,
                updated_at=item.updated_at
            )
            job_aggregates.append(job_aggregate)
        return job_aggregates
