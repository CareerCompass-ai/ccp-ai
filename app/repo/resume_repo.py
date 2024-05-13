from config.postgres import SessionLocal
from sqlalchemy.orm import Session

from models.ccp_resume import Resume
from app.dto import resume
from typing import List, Optional

class ResumeRepository:
    def __init__(self):
        self.db = SessionLocal()

    def get_by_id(self, id):
        result = self.db.query(Resume).filter(Resume.id == id).first()
        return result
    
    async def post_resume(self, db:Session, input: Optional[resume.ResumeBase]):
        if input:
            resume_instance = Resume(**input.model_dump())
            resume_instance.id = None
            self.db.add(resume_instance)
            self.db.commit()
            self.db.refresh(resume_instance)

            db.close()
            return resume_instance
        
    async def get_by_user_id(self, db:Session, user_id) -> List[Resume]:
        result = self.db.query(Resume).filter(Resume.candidate_id == user_id).all()

        db.close()
        return result
