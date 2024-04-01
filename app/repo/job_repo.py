from config.postgres import SessionLocal
from typing import List, Optional
from models.ccp_job import Job
from app.dto import job
class JobRepository:
    def __init__(self):
        self.db = SessionLocal()

    def get_by_id(self, id):
        return self.db.query(Job).filter(Job.id == id).first()
    
    def post_job(self, input: Optional[job.JobBase]):
        if input:
            job_instance = Job(**input.model_dump())
            job_instance.id = None
            self.db.add(job_instance)
            self.db.commit()
            self.db.refresh(job_instance)
            return job_instance