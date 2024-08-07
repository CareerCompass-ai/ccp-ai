from sqlalchemy.orm import Session
from typing import Optional
from models.ccp_application import Application


class ApplicationRepository:
    async def get_job_ids_by_resume_id(self, db:Session, resume_id):
        job_ids = (
            db.query(Application.job_id)
            .filter(Application.resume_id == resume_id)
            .all()
        )
        
        return [job_id for (job_id,) in job_ids]
    
    async def create(self, session: Session, record: Application) -> Application:
        session.add(record)
        session.flush()
        session.refresh(record)

        return record
    
    async def list_by_resume_ids(self, db:Session, resume_ids: list[int], job_id: int) -> list[Application]:
        applications = (
            db.query(Application).
            filter(Application.resume_id.in_(resume_ids), Application.job_id == job_id).
            all()
        )
        
        return applications
    
    async def list_resume_ids_by_job_id(self, db:Session, job_id: int) -> list[int]:
        resume_ids = (
            db.query(Application.resume_id).
            filter(Application.job_id == job_id).
            all()
        )
        
        return [resume_id for (resume_id,) in resume_ids]

    async def update_with_map(self, db:Session, job_id: int, resume_id: int, props: dict) -> Optional[Application]:
        record = db.query(Application).filter(Application.job_id == job_id, Application.resume_id == resume_id).first()
        if not record:
            return None
        
        for key, val in props.items():
            if hasattr(record, key):
                setattr(record, key, val)
        
        db.commit()
        db.refresh(record)
        return record