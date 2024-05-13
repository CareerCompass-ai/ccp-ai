from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc

from config.postgres import SessionLocal
from models.ccp_job import Job
from app.dto import job

class JobRepository:
    def __init__(self):
        self.db = SessionLocal()

    def get_by_id(self, id):
        data = self.db.query(Job).filter(Job.id == id).first()

        self.db.close()

        return data
    
    def create(self, session: Session, record: Optional[job.JobBase]) -> Optional[Job]:
        if record:
            record = Job(**record.model_dump())
            session.add(record)
            session.flush()  
            session.refresh(record)  

            return record
        
        return None
    
    def update_with_map(self, record: Job, props: dict) -> Job:
        for key, val in props.items():
            setattr(record, key, val)

            self.db.commit()
            self.db.refresh(record)

    def get_latest_job(self) -> Optional[Job]:
        return self.db.query(Job).order_by(desc(Job.updated_at)).first()