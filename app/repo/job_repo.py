from typing import Optional

from sqlalchemy import desc
from sqlalchemy.orm import Session

from app.dto import job, mapper
from app.dto.job import JobForSEO
from models.ccp_job import Job
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException, status
from pkg.logging import logger


class JobRepository:
    async def get_by_id(self, db:Session, id) -> Optional[Job]:
        data = db.query(Job).filter(Job.id == id).first()
        return data
    
    async def create(self, session: Session, record: Optional[job.JobBase]) -> Optional[Job]:
        try:
            record = Job(**record.model_dump())
            session.add(record)
            session.flush()  
            session.refresh(record)
            return record
        except SQLAlchemyError as e:  
            logger.error(f"create_job failed error = {e}")
            raise 
    
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
    
    async def get_job_title(self, db: Session, job_id: int):
        res = db.query(Job.job_title).filter(Job.id == job_id).first()

        return res.job_title
    
    async def list_posted_job(self, db: Session, recruiter_id: int, input: str, limit: int, offset: int, is_hiring: bool = None):
        query = db.query(Job.id).filter(Job.recruiter_id == recruiter_id, Job.job_title.ilike(f"%{input}%"), Job.is_hiring == is_hiring)
        
        total_records = query.count()
        data = query.order_by(desc(Job.updated_at)).offset(offset).limit(limit).all()

        return total_records, data
    
    async def list_all_jobs_for_seo(self, db: Session):
        result = db.query(Job.id, Job.job_title).all()
        return [JobForSEO(id=job.id, title=job.job_title) for job in result]
    
    async def check_by_recruiter_id(self, db:Session, job_id: int, recruiter_id: int):
        data = db.query(Job).filter(Job.id == job_id, Job.recruiter_id == recruiter_id).first()
        return data