from config.postgres import SessionLocal
from sqlalchemy.orm import Session

from models.ccp_resume import Resume
from app.dto import resume
from typing import List, Optional

class ResumeRepository:
    async def get_by_id(self, db:Session, id):
        result = db.query(Resume).filter(Resume.id == id).first()
        return result
    
    async def post_resume(self, db:Session, input: Optional[resume.ResumeBase]):
        if input:
            resume_instance = Resume(**input.model_dump())
            resume_instance.id = None
            db.add(resume_instance)
            db.flush()
            db.refresh(resume_instance)
            return resume_instance
        
        return None
        
    async def get_by_user_id(self, db:Session, user_id) -> List[Resume]:
        result = db.query(Resume).filter(Resume.candidate_id == user_id, Resume.active == True).all()
        return result
    
    async def update_with_map(self, db:Session, resume_id: int, props: dict) -> Optional[Resume]:
        resume_record = db.query(Resume).filter(Resume.id == resume_id).first()
        if not resume_record:
            return None
        
        for key, val in props.items():
            if hasattr(resume_record, key):
                setattr(resume_record, key, val)
        
        db.commit()
        db.refresh(resume_record)
        return resume_record
