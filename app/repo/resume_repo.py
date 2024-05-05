from config.postgres import SessionLocal

from models.ccp_resume import Resume
from app.dto import resume
from typing import List, Optional

class ResumeRepository:
    def __init__(self):
        self.db = SessionLocal()

    def get_by_id(self, id):
        result = self.db.query(Resume).filter(Resume.id == id).first()
        return result
    
    def post_resume(self, input: Optional[resume.ResumeBase]):
        if input:
            resume_instance = Resume(**input.model_dump())
            resume_instance.id = None
            self.db.add(resume_instance)
            self.db.commit()
            self.db.refresh(resume_instance)
            return resume_instance
        
    def get_by_user_id(self, user_id) -> List[Resume]:
        result = self.db.query(Resume).filter(Resume.candidate_id == user_id).all()
        return result
