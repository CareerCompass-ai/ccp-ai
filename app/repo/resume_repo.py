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
    
    async def post_resume(self, input: Optional[resume.ResumeBase]):
        if input:
            resume_instance = Resume(**input.model_dump())
            resume_instance.id = None
            self.db.add(resume_instance)
            self.db.commit()
            self.db.refresh(resume_instance)

            self.db.close()
            return resume_instance
        
    async def get_by_user_id(self, user_id) -> List[Resume]:
        result = self.db.query(Resume).filter(Resume.candidate_id == user_id, Resume.active == True).all()

        self.db.close()
        return result
    
    def update_with_map(self, resume_id: int, props: dict) -> Optional[Resume]:
        with SessionLocal() as session:
            resume_record = session.query(Resume).filter(Resume.id == resume_id).first()
            if not resume_record:
                return None
            
            for key, val in props.items():
                if hasattr(resume_record, key):
                    setattr(resume_record, key, val)
            
            session.commit()
            session.refresh(resume_record)
            return resume_record
