from config.postgres import SessionLocal
from sqlalchemy.orm import Session
from typing import Optional
from models.ccp_job import Job
from app.dto import job

class JobRepository:
    def __init__(self):
        self.db = SessionLocal()

    def get_by_id(self, id):
        return self.db.query(Job).filter(Job.id == id).first()
    
    def create(self, session: Session, record: Optional[job.JobBase]) -> Optional[Job]:
        if record:
            record = Job(**record.model_dump())
            session.add(record)
            session.flush()  
            session.refresh(record)  

            return record
        
        return None