from typing import Optional

from sqlalchemy import desc
from sqlalchemy.orm import Session

from app.dto import job
from config.postgres import SessionLocal
from models.ccp_job import Job


class JobRepository:
    async def get_by_id(self, db:Session, id) -> Optional[Job]:
        data = db.query(Job).filter(Job.id == id).first()
        return data
    
    async def create(self, session: Session, record: Optional[job.JobBase]) -> Optional[Job]:
        if record:
            record = Job(**record.model_dump())
            session.add(record)
            session.flush()  
            session.refresh(record)  

            return record
        
        return None
    
    async def update_with_map(self, db:Session, job_id: int, props: dict) -> Optional[Job]:
        job_record = db.query(Job).filter(Job.id == job_id).first()
        if not job_record:
            return None
        
        for key, val in props.items():
            if hasattr(job_record, key):
                setattr(job_record, key, val)
        
        db.commit()
        db.refresh(job_record)
        return job_record

    async def get_latest_job(self, db: Session) -> Optional[Job]:
        return db.query(Job).order_by(desc(Job.id)).first()    
    
    async def get_file_name(self, db:Session, job_id: int):
        data = db.query(Job.file_name).filter(Job.id == job_id).first()

        return data.file_name