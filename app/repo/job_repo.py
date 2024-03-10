from config.postgres import SessionLocal
from sqlalchemy.orm import Session
from models import ccp_job
from models.ccp_job import Job


class JobRepository:
    def __init__(self):
        self.db = SessionLocal()

    def get_by_id(self, id):
        return self.db.query(Job).filter(Job.id == id).first()
    
    def get_jobs(db: Session):
        return db.query(ccp_job.Job).all()
